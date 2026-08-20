EXEC sp_configure 'clr enabled', 1;
RECONFIGURE;
CREATE ASSEMBLY Helper FROM 'C:\bin\helper.dll';
