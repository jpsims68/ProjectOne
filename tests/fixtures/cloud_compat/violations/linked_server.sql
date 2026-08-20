EXEC sp_addlinkedserver @server = N'REMOTE1';
SELECT * FROM OPENQUERY(REMOTE1, 'SELECT 1');
SELECT * FROM REMOTE1.OtherDb.dbo.Customers;
