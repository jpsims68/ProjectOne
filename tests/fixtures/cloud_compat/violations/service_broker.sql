CREATE QUEUE dbo.EventQueue;
CREATE SERVICE EventService ON QUEUE dbo.EventQueue;
