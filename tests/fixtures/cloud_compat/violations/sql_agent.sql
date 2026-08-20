EXEC msdb.dbo.sp_add_job @job_name = N'NightlyLoad';
EXEC msdb.dbo.sp_add_jobstep @job_name = N'NightlyLoad', @step_name = N'Run';
