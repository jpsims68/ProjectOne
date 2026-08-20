EXEC xp_cmdshell 'dir C:\';
EXEC msdb.dbo.sp_send_dbmail @subject = N'done';
