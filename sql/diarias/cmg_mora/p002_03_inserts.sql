USE DW_Raw_v2
GO


SELECT 
    '
	INSERT INTO [storage].[com_act].[SBTVRIE001] VALUES (' + 
    '''' + CONVERT(VARCHAR(25), SFECPRO, 121) + ''',' + 
    CAST(STIPCOD AS VARCHAR(50)) + ', ' +
    '''' + REPLACE(SCODREL, '''', '''''') + ''', ' +
    CAST(CAST(SMONREC AS DECIMAL(20,7)) AS VARCHAR(50))  + ', ' +
    CAST(CAST(STASREC AS DECIMAL(20,7)) AS VARCHAR(50))  + ', ' +
    CAST(SRECCAST12M AS VARCHAR(50)) + ', ' +    
    CAST(SSTKPROV AS VARCHAR(50)) + ', ' +    
    CAST(SGASPROVCART AS VARCHAR(50)) + ', ' +    
    CAST(SGASPROVCONTA AS VARCHAR(50)) + ', ' +    
    CAST(SGASPROVOM3155 AS VARCHAR(50)) + ', ' +    
    CAST(SGASPROVVOLU AS VARCHAR(50)) + ', ' +    
    CAST(SGASPROVBRUTO AS VARCHAR(50)) + ', ' +    
    CAST(SGASPROVBRUTO12M AS VARCHAR(50)) +    
    ');' AS Inserts
FROM 
    DW_Raw_v2.dbo.CMGMora_Recaudo;



