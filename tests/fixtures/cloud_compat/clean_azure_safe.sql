-- Deliberately mentions USE, sp_configure, OPENQUERY and CREATE ASSEMBLY in
-- comments only. A check that matched raw text would flag this file.
/* Also blocked: BACKUP DATABASE, xp_cmdshell, FILESTREAM. */
CREATE SCHEMA mining;
GO
CREATE TABLE mining.EventLog (
    EventLogId  BIGINT        NOT NULL IDENTITY(1,1),
    CaseId      NVARCHAR(128) NOT NULL,
    Activity    NVARCHAR(256) NOT NULL,
    OccurredAt  DATETIME2(3)  NOT NULL,
    CONSTRAINT PK_EventLog PRIMARY KEY CLUSTERED (EventLogId)
);
GO
-- Same-database three-part name is legal on Azure SQL Database.
SELECT COUNT(*) FROM mvp.mining.EventLog;
-- tempdb three-part name is legal.
SELECT * FROM tempdb.sys.objects;
-- A string literal naming a blocked construct must not trip the check.
INSERT INTO mining.EventLog (CaseId, Activity, OccurredAt)
VALUES (N'C-1', N'sp_add_job was rejected during review', SYSUTCDATETIME());
