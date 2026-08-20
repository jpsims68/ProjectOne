#!/usr/bin/env python3
"""
Governance check — Azure SQL Database compatibility (FR-010).

Scans SQL for capabilities that do NOT exist in Azure SQL Database. The owner's
local instance is SQL Server 2022 Developer Edition — the full Enterprise feature
set — so any of these will run perfectly on the developer machine and fail only at
deployment. Local success is therefore not evidence of deployability.

This is the CP-004 design tax made enforceable: while OQ-13 is open between Azure
SQL Database and Managed Instance, nothing may depend on a capability the more
restrictive target lacks. Coding to the Azure SQL Database floor keeps that
decision genuinely open. Using an MI-only capability closes it silently.

SCOPE OF THE BLOCK LIST
FR-010 names four families (SQL Agent, cross-database three-part names, linked
servers, CLR). Those are illustrative of its stated objective — "capabilities
absent from Azure SQL Database" — not a definition of it. Implementing only the
four would satisfy FR-010's acceptance test while missing its purpose. The list
below is built from the objective and verified against Microsoft's T-SQL
differences reference (last reviewed 2026-04-02).

NOT A DATABASE OPERATION
This check reads files. It never connects to an instance, never executes SQL, and
never changes a server setting. Local SQL Server keeps every feature it has.

Exit 0 = clean. Exit 1 = violation or unexpected state.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Directories scanned. Kept narrow deliberately: SQL that is genuinely local-only
# and not part of the deployable product can live outside these paths without
# tripping the check. Widening this to "every .sql in the repository" would flag
# such scripts and train the reader to disregard the check.
SCAN_DIRS = [ROOT / "db"]

SQL_SUFFIXES = {".sql"}

# Three-part names are NOT uniformly illegal. Microsoft: "Three part names
# referencing the tempdb database and the current database are supported." So a
# rule flagging every three-part name would false-positive on ordinary
# same-database references. Only prefixes outside this set are treated as
# cross-database.
CURRENT_DB_NAMES = {"tempdb", "mvp"}

Rule = tuple[str, re.Pattern[str], str]

RULES: list[Rule] = [
    (
        "USE-STATEMENT",
        re.compile(r"^\s*USE\s+[\[\w]", re.IGNORECASE | re.MULTILINE),
        "USE is not supported. Changing database context requires a new connection.",
    ),
    (
        "SQL-AGENT",
        re.compile(
            r"\b(msdb\s*\.|sp_add_job\b|sp_add_jobstep\b|sp_add_jobschedule\b|"
            r"sp_add_schedule\b|sp_update_job\b|sp_start_job\b|sysjobs\b|"
            r"sp_add_alert\b|sp_add_operator\b|sp_add_notification\b)",
            re.IGNORECASE,
        ),
        "SQL Server Agent and msdb are absent. Use an external scheduler.",
    ),
    (
        "LINKED-SERVER",
        re.compile(
            r"\b(sp_addlinkedserver\b|sp_addlinkedsrvlogin\b|sp_serveroption\b|"
            r"OPENQUERY\s*\(|OPENDATASOURCE\s*\(|OPENROWSET\s*\(\s*'SQLNCLI|"
            r"OPENROWSET\s*\(\s*'MSOLEDBSQL)",
            re.IGNORECASE,
        ),
        "Linked servers, OPENQUERY and OPENDATASOURCE are not supported.",
    ),
    (
        "CLR",
        re.compile(
            r"\b(CREATE\s+ASSEMBLY\b|ALTER\s+ASSEMBLY\b|EXTERNAL\s+NAME\b|"
            r"'clr[\s_]enabled')",
            re.IGNORECASE,
        ),
        "CLR integration is not available in Azure SQL Database.",
    ),
    (
        "FILE-PLACEMENT",
        re.compile(
            r"\b(FILESTREAM\b|FILETABLE\b|FILEGROUP\b|ADD\s+FILE\b|"
            r"PRIMARY\s*\(\s*NAME\s*=|LOG\s+ON\s*\(|FILENAME\s*=)",
            re.IGNORECASE,
        ),
        "File placement, FILESTREAM and FILETABLE are managed by the service.",
    ),
    (
        "BACKUP-RESTORE-HA",
        re.compile(
            r"^\s*(BACKUP|RESTORE)\s+(DATABASE|LOG|FILELISTONLY|HEADERONLY)\b"
            r"|\bCREATE\s+AVAILABILITY\s+GROUP\b|\bSET\s+PARTNER\b"
            r"|\bSET\s+RECOVERY\s+(FULL|SIMPLE|BULK_LOGGED)\b",
            re.IGNORECASE | re.MULTILINE,
        ),
        "Backup, restore, mirroring and recovery models are service-managed.",
    ),
    (
        "INSTANCE-CONFIG",
        re.compile(
            r"\b(sp_configure\b|RECONFIGURE\b|DBCC\s+TRACE(ON|OFF)\b|"
            r"CREATE\s+RESOURCE\s+POOL\b|CREATE\s+WORKLOAD\s+GROUP\b|"
            r"ALTER\s+SERVER\s+CONFIGURATION\b|^\s*SHUTDOWN\b)",
            re.IGNORECASE | re.MULTILINE,
        ),
        "Instance configuration is not exposed. Use ALTER DATABASE SCOPED CONFIGURATION.",
    ),
    (
        "EXTENDED-PROC",
        re.compile(r"\b(xp_cmdshell\b|xp_sendmail\b|sp_send_dbmail\b|sp_addextendedproc\b)"),
        "Extended stored procedures and Database Mail are not supported.",
    ),
    (
        "SERVER-SCOPE",
        re.compile(
            r"\b(CREATE\s+ENDPOINT\b|ON\s+ALL\s+SERVER\b|CREATE\s+SERVER\s+AUDIT\b|"
            r"CREATE\s+CREDENTIAL\b|EXECUTE\s+AS\s+LOGIN\b|CREATE\s+SERVER\s+ROLE\b|"
            r"sp_addmessage\b|SET\s+REMOTE_PROC_TRANSACTIONS\b)",
            re.IGNORECASE,
        ),
        "Server-scoped objects, endpoints and logon triggers are not supported.",
    ),
    (
        "WINDOWS-AUTH",
        re.compile(r"\bCREATE\s+LOGIN\b[^;]{0,200}?\bFROM\s+WINDOWS\b", re.IGNORECASE | re.DOTALL),
        "Windows authentication is not supported. Use Microsoft Entra identities.",
    ),
    (
        "SERVICE-BROKER",
        re.compile(
            r"\b(CREATE\s+QUEUE\b|CREATE\s+SERVICE\b|CREATE\s+MESSAGE\s+TYPE\b|"
            r"CREATE\s+CONTRACT\b|BEGIN\s+DIALOG\b|ENABLE_BROKER\b)",
            re.IGNORECASE,
        ),
        "Service Broker is not available in Azure SQL Database.",
    ),
    (
        "TRUSTWORTHY",
        re.compile(r"\bSET\s+TRUSTWORTHY\s+ON\b|\bDB_CHAINING\s+ON\b", re.IGNORECASE),
        "TRUSTWORTHY and cross-database ownership chaining are not supported.",
    ),
    (
        "DISTRIBUTED-TXN",
        re.compile(r"\bBEGIN\s+DISTRIBUTED\s+TRAN(SACTION)?\b", re.IGNORECASE),
        "Distributed transactions are not supported.",
    ),
    (
        "BULK-INSERT-LOCAL",
        re.compile(r"\bBULK\s+INSERT\b[^;]{0,400}?FROM\s+'[A-Za-z]:\\", re.IGNORECASE | re.DOTALL),
        "BULK INSERT from a local filesystem path is not supported; use Azure Blob Storage.",
    ),
]

FOUR_PART = re.compile(r"\b\w+\.\w+\.\w+\.\w+\b")
THREE_PART = re.compile(r"\b(\w+)\.(\w+)\.(\w+)\b")


def strip_noncode(text: str) -> str:
    """Blank out comments and string literals, preserving line numbering.

    Matching raw text would flag a rule named in a comment or a message string,
    producing violations no engine would ever execute. Characters are replaced
    with spaces rather than removed so reported line numbers stay accurate.
    """
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        two = text[i : i + 2]
        if two == "--":
            while i < n and text[i] != "\n":
                out[i] = " "
                i += 1
        elif two == "/*":
            depth = 1
            out[i] = out[i + 1] = " "
            i += 2
            while i < n and depth:
                if text[i : i + 2] == "*/":
                    depth -= 1
                    out[i] = out[i + 1] = " "
                    i += 2
                elif text[i : i + 2] == "/*":
                    depth += 1
                    out[i] = out[i + 1] = " "
                    i += 2
                else:
                    if text[i] != "\n":
                        out[i] = " "
                    i += 1
        elif text[i] == "'":
            out[i] = " "
            i += 1
            while i < n:
                if text[i] == "'" and text[i : i + 2] != "''":
                    out[i] = " "
                    i += 1
                    break
                if text[i] != "\n":
                    out[i] = " "
                i += 1
        else:
            i += 1
    return "".join(out)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan_text(text: str, label: str) -> list[str]:
    code = strip_noncode(text)
    found: list[str] = []

    for name, pattern, advice in RULES:
        for m in pattern.finditer(code):
            found.append(f"[{name}] {label}:{line_of(code, m.start())} — {advice}")

    for m in FOUR_PART.finditer(code):
        found.append(
            f"[FOUR-PART-NAME] {label}:{line_of(code, m.start())} — "
            f"'{m.group(0)}' is a four-part name; cross-instance references are not supported."
        )

    for m in THREE_PART.finditer(code):
        # Skip anything already inside a four-part name — it is reported above.
        if FOUR_PART.search(code, max(0, m.start() - 40), m.end() + 40):
            continue
        db = m.group(1).lower()
        if db in CURRENT_DB_NAMES:
            continue
        found.append(
            f"[CROSS-DATABASE] {label}:{line_of(code, m.start())} — "
            f"'{m.group(0)}' references database '{m.group(1)}'. Only the current database "
            f"and tempdb may be referenced by three-part name."
        )
    return found


def sql_files(base: pathlib.Path) -> list[pathlib.Path]:
    """Resolve a target to the SQL files it contains.

    A target may be a directory or a single file. Handling only directories made
    a file argument scan nothing and report PASS — the skip-and-pass pattern this
    check exists to prevent, found by the fixture harness on its first run.
    """
    if base.is_file():
        return [base] if base.suffix.lower() in SQL_SUFFIXES else []
    return sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in SQL_SUFFIXES)


def scan_path(base: pathlib.Path) -> list[str]:
    viol: list[str] = []
    for p in sql_files(base):
        rel = p.relative_to(ROOT) if ROOT in p.parents else p
        viol.extend(scan_text(p.read_text(encoding="utf-8", errors="ignore"), str(rel)))
    return viol


def main(argv: list[str]) -> int:
    print("=" * 72)
    print("GOVERNANCE CHECK — Azure SQL Database compatibility (FR-010)")
    print("=" * 72)

    targets = [pathlib.Path(a) for a in argv[1:]] or SCAN_DIRS
    present = [t for t in targets if t.exists()]

    if not present:
        # Absent-expected, asserted rather than assumed. No DDL exists yet and
        # production implementation is NOT AUTHORIZED, so an empty scope is the
        # correct state today. This branch must NOT be reused to excuse a missing
        # directory once DDL exists — that would be skip-and-pass.
        named = ", ".join(
            str(t.relative_to(ROOT)) if ROOT in t.parents else str(t) for t in targets
        )
        print(f"\nSTATE: ABSENT-EXPECTED — no SQL scope present ({named}).")
        print("No DDL has been committed. The check is live and will scan it when it appears.")
        print("\nRESULT: PASS — nothing to scan, and nothing was expected")
        return 0

    viol: list[str] = []
    for t in present:
        viol.extend(scan_path(t))

    scanned = sum(len(sql_files(t)) for t in present)
    print(f"\nSQL files scanned: {scanned}")

    if viol:
        print(f"\nviolations: {len(viol)}\n")
        for v in viol:
            print(f"  ! {v}")
        print("\nThese run on SQL Server 2022 Developer Edition and fail on Azure SQL Database.")
        print("Local success is not evidence of deployability (CP-004 / OQ-13 design tax).")
        print("\nRESULT: FAIL")
        return 1

    print("\nRESULT: PASS — no Azure SQL Database incompatibilities detected")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
