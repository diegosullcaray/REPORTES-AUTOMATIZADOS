par alo que es el sin asiganr diario 
Sub ActualizarSQL_AmbasHojas()
    Dim strFecha As String
    Dim strSQL As String
    Dim lo As ListObject
    Dim conn As WorkbookConnection
    Dim pt As PivotTable
    Dim pc As PivotCache
    Dim fechaCalculada As Date
    Dim rutaLogoLocal As String
    Dim urlWebhook As String
    
    ' ==========================================
    ' CONFIGURACIÓN: RUTAS Y WEBHOOK
    ' ==========================================
    rutaLogoLocal = "D:\FINANCIERA CONFIANZA\03 RECURSOS\logo.png"
    urlWebhook = "https://chat.googleapis.com/v1/spaces/AAQAmeym9-k/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=sKoJT9awQOo0RMoAsEQP1rcY_EztBtmtVS7yqiZlPsg"
    
    ' ==========================================
    ' 0. FECHA AUTOMÁTICA (DÍA ANTERIOR)
    ' ==========================================
    fechaCalculada = Date - 1
    ThisWorkbook.Sheets("FILTRO").Range("B1").Value = fechaCalculada
    strFecha = Format(fechaCalculada, "yyyy-mm-dd")
    ThisWorkbook.Save
    
    ' ==========================================
    ' 1. CONSTRUIR LA CONSULTA SQL
    ' ==========================================
    strSQL = "SET NOCOUNT ON; " & vbCrLf
    strSQL = strSQL & "IF OBJECT_ID('tempdb..#SECVAL') IS NOT NULL DROP TABLE #SECVAL; " & vbCrLf
    strSQL = strSQL & "SELECT SCODSEC INTO #SECVAL FROM storage.[com_act].SDAS001 WHERE SFECPRO= '" & strFecha & "' "
    strSQL = strSQL & "EXCEPT "
    strSQL = strSQL & "SELECT RCODSEC FROM storage.ref.FJERCOR02('" & strFecha & "'); " & vbCrLf
    strSQL = strSQL & "CREATE CLUSTERED INDEX IX_Temp_Vendedor ON #SECVAL(SCODSEC); " & vbCrLf
    strSQL = strSQL & ";WITH cta_a AS ( " & vbCrLf
    strSQL = strSQL & "  SELECT HSALCAPMN, HCODSEC, HSUCCLI, HASEOPER, HCTACLI, HDESCLI, HCODOPE, HCODMOD, HTIPOPE, HSUBTIP "
    strSQL = strSQL & "  FROM storage.[com_act].HCDA001 WHERE HFECPRO = '" & strFecha & "' "
    strSQL = strSQL & ") " & vbCrLf
    strSQL = strSQL & "SELECT 'FC' AS NIVEL, A.HASEOPER AS Asesor_Operativo, A.HCTACLI AS Cuenta_Cliente, "
    strSQL = strSQL & "A.HDESCLI AS Nom_Cliente, A.HCODOPE AS Operacion, A.HSALCAPMN AS Saldo_Capital, "
    strSQL = strSQL & "_P3.RDESGRU02 AS Grupo, ISNULL(C.RDESTER,'NULL') AS Territorio, C.RDESCOR AS Corredor, "
    strSQL = strSQL & "C.RDESAGE AS Agencia_Cli, B.RDESUNI AS Unidad_Negocio " & vbCrLf
    strSQL = strSQL & "FROM cta_a A " & vbCrLf
    strSQL = strSQL & "LEFT JOIN (SELECT * FROM storage.ref.FJERCOR02('" & strFecha & "')) B ON A.HCODSEC = B.RCODSEC " & vbCrLf
    strSQL = strSQL & "LEFT JOIN storage.ref.vjercor03 C ON A.HSUCCLI = C.RCODAGE " & vbCrLf
    strSQL = strSQL & "LEFT JOIN STORAGE.[COM_ACT].RETP002 _P2 ON A.HCODMOD=_P2.RCODMOD AND A.HTIPOPE=_P2.RTIPOPE AND _P2.RSUBTIP=A.HSUBTIP " & vbCrLf
    strSQL = strSQL & "LEFT JOIN STORAGE.[COM_ACT].RETP001 _P1 ON A.HCODMOD=_P1.RCODMOD AND A.HTIPOPE=_P1.RTIPOPE " & vbCrLf
    strSQL = strSQL & "LEFT JOIN STORAGE.[COM_ACT].RETP003 _P3 ON ISNULL(_P2.RCODPROD,_P1.RCODPROD)=_P3.RCODPROD " & vbCrLf
    strSQL = strSQL & "WHERE A.HASEOPER IN ('','--') OR A.HASEOPER IS NULL " & vbCrLf
    strSQL = strSQL & "OR EXISTS (SELECT 1 FROM #SECVAL t1 WHERE t1.SCODSEC=A.HASEOPER) " & vbCrLf
    strSQL = strSQL & "ORDER BY C.RCODTER, C.RCODCOR, C.RDESAGE; " & vbCrLf
    strSQL = strSQL & "DROP TABLE #SECVAL;"
    
    ' ==========================================
    ' 2. ACTUALIZAR TABLA NORMAL EN DATA_MIS_v2
    ' ==========================================
    On Error Resume Next
    Set lo = ThisWorkbook.Sheets("DATA_MIS_v2").ListObjects(1)
    On Error GoTo 0
    
    If Not lo Is Nothing Then
        On Error Resume Next
        Set conn = lo.QueryTable.WorkbookConnection
        On Error GoTo 0
        If Not conn Is Nothing Then
            If conn.Type = xlConnectionTypeODBC Then
                conn.ODBCConnection.CommandType = xlCmdSql
                conn.ODBCConnection.CommandText = strSQL
                conn.ODBCConnection.BackgroundQuery = False
                conn.Refresh
            ElseIf conn.Type = xlConnectionTypeOLEDB Then
                conn.OLEDBConnection.CommandType = xlCmdSql
                conn.OLEDBConnection.CommandText = strSQL
                conn.OLEDBConnection.BackgroundQuery = False
                conn.Refresh
            End If
        End If
    End If
    
    ' ==========================================
    ' 3. ACTUALIZAR TABLA DINÁMICA EN RESUMEN_v2
    ' ==========================================
    On Error Resume Next
    Set pt = ThisWorkbook.Sheets("RESUMEN_v2").PivotTables(1)
    On Error GoTo 0
    
    If Not pt Is Nothing Then
        On Error Resume Next
        Set pc = pt.PivotCache
        pc.BackgroundQuery = False
        pc.CommandText = strSQL
        pc.Refresh
        On Error GoTo 0
    End If
    
    DoEvents
    Application.Wait (Now + TimeValue("0:00:03"))

    ' ==========================================
    ' 4. EXPORTAR TABLA DINÁMICA COMO IMAGEN JPG
    ' ==========================================
    Dim rutaImagen As String
    Dim chartObj As ChartObject
    Dim wsResumen As Worksheet
    
    Set wsResumen = ThisWorkbook.Sheets("RESUMEN_v2")
    rutaImagen = Environ("TEMP") & "\Reporte_Temporal.jpg"
    
    If Not pt Is Nothing Then
        wsResumen.Activate
        pt.TableRange2.Select
        Selection.CopyPicture Appearance:=xlScreen, Format:=xlBitmap
        
        Set chartObj = wsResumen.ChartObjects.Add(Left:=10, Top:=10, Width:=pt.TableRange2.Width, Height:=pt.TableRange2.Height)
        chartObj.Activate
        DoEvents
        chartObj.Chart.Paste
        DoEvents
        chartObj.Chart.Export Filename:=rutaImagen, FilterName:="JPG"
        chartObj.Delete
    End If

    ' ==========================================
    ' 5. CONCATENAR CORREOS DE LA HOJA "CORREOS"
    ' ==========================================
    Dim wsCorreos As Worksheet
    Dim filaActual As Long
    Dim listaPara As String
    
    On Error Resume Next
    Set wsCorreos = ThisWorkbook.Sheets("CORREOS")
    On Error GoTo 0
    
    If wsCorreos Is Nothing Then
        MsgBox "No se encontró la hoja 'CORREOS'. Revisa el nombre.", vbCritical, "Error"
        Exit Sub
    End If
    
    listaPara = ""
    filaActual = 2
    
    ' Unir todos los destinatarios separados por punto y coma (;)
    Do While wsCorreos.Cells(filaActual, 1).Value <> ""
        If Trim(wsCorreos.Cells(filaActual, 1).Value) <> "" Then
            If listaPara = "" Then
                listaPara = Trim(wsCorreos.Cells(filaActual, 1).Value)
            Else
                listaPara = listaPara & ";" & Trim(wsCorreos.Cells(filaActual, 1).Value)
            End If
        End If
        filaActual = filaActual + 1
    Loop
    
    If listaPara = "" Then
        MsgBox "La lista de correos está vacía.", vbExclamation, "Atención"
        Exit Sub
    End If

    ' ==========================================
    ' 6. ENVÍO DE UN ÚNICO CORREO EN BLOQUE (CDO)
    ' ==========================================
    Dim iMsg As Object
    Dim iConf As Object
    Dim Flds As Object
    Dim adjuntoImagen As Object
    Dim adjuntoLogo As Object
    Dim rutaCopiaExcel As String
    Dim nombreNuevoExcel As String
    Dim htmlBodyContent As String
    
    nombreNuevoExcel = "Cartera-Sin asignar-" & strFecha & ".xlsm"
    
    ThisWorkbook.Save
    rutaCopiaExcel = Environ("TEMP") & "\" & nombreNuevoExcel
    ThisWorkbook.SaveCopyAs rutaCopiaExcel

    Set iMsg = CreateObject("CDO.Message")
    Set iConf = CreateObject("CDO.Configuration")
    Set Flds = iConf.Fields

    With Flds
        .Item("http://schemas.microsoft.com/cdo/configuration/sendusing") = 2
        .Item("http://schemas.microsoft.com/cdo/configuration/smtpserver") = "smtp.gmail.com"
        .Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport") = 465
        .Item("http://schemas.microsoft.com/cdo/configuration/smtpusessl") = True
        .Item("http://schemas.microsoft.com/cdo/configuration/smtpauthenticate") = 1
        .Item("http://schemas.microsoft.com/cdo/configuration/sendusername") = "mis@confianza.pe"
        .Item("http://schemas.microsoft.com/cdo/configuration/sendpassword") = "ogqqcbsjsbftxbix"
        .Update
    End With

    ' HTML del Cuerpo del Correo
    htmlBodyContent = "<html><body style='font-family: Arial, sans-serif; font-size: 13px; color: #333;'>"
    htmlBodyContent = htmlBodyContent & "Buenos días,<br><br>"
    htmlBodyContent = htmlBodyContent & "Adjunto la tabla resumen y el archivo correspondiente a los datos del <b>" & strFecha & "</b>:<br><br>"
    htmlBodyContent = htmlBodyContent & "<img src='cid:Reporte_Temporal.jpg'><br><br>"
    htmlBodyContent = htmlBodyContent & "Saludos cordiales,<br><br>"
    
    ' Tabla de la Firma
    htmlBodyContent = htmlBodyContent & "<table border='0' cellspacing='0' cellpadding='0'>"
    htmlBodyContent = htmlBodyContent & "  <tr>"
    htmlBodyContent = htmlBodyContent & "    <td style='padding-right:15px; vertical-align:middle;'>"
    If Dir(rutaLogoLocal) <> "" Then
        htmlBodyContent = htmlBodyContent & "      <img src='cid:Logo_Confianza.jpg' width='180'>"
    End If
    htmlBodyContent = htmlBodyContent & "    </td>"
    htmlBodyContent = htmlBodyContent & "    <td style='border-left: 2px solid #005696; padding-left: 15px; vertical-align: top; font-size: 12px; color: #005696;'>"
    htmlBodyContent = htmlBodyContent & "      <b style='font-size: 13px; color: #0081c6;'>Sistemas de Información de Gestión</b><br>"
    htmlBodyContent = htmlBodyContent & "      Las Begonias 441, Ofi. 238C, San Isidro<br>"
    htmlBodyContent = htmlBodyContent & "      Edificio Plaza del Sol - San Isidro<br>"
    htmlBodyContent = htmlBodyContent & "      Lima - Perú<br>"
    htmlBodyContent = htmlBodyContent & "      <a href='https://www.confianza.pe' style='font-weight:bold; color:#003366;'>www.confianza.pe</a>"
    htmlBodyContent = htmlBodyContent & "    </td>"
    htmlBodyContent = htmlBodyContent & "  </tr>"
    htmlBodyContent = htmlBodyContent & "</table>"
    htmlBodyContent = htmlBodyContent & "</body></html>"

    With iMsg
        Set .Configuration = iConf
        .To = listaPara ' <--- Aquí envía a la lista completa en un solo mensaje
        .From = "Sistemas de Información de Gestión <mis@confianza.pe>"
        .Subject = "Reporte Sin Asignar - " & strFecha
        .HTMLBody = htmlBodyContent
        
        ' 1. Captura de la Tabla Resumen
        Set adjuntoImagen = .AddAttachment(rutaImagen)
        adjuntoImagen.Fields.Item("urn:schemas:mailheader:Content-ID") = "<Reporte_Temporal.jpg>"
        adjuntoImagen.Fields.Update
        
        ' 2. Logo Local para la Firma
        If Dir(rutaLogoLocal) <> "" Then
            Set adjuntoLogo = .AddAttachment(rutaLogoLocal)
            adjuntoLogo.Fields.Item("urn:schemas:mailheader:Content-ID") = "<Logo_Confianza.jpg>"
            adjuntoLogo.Fields.Update
        End If
        
        ' 3. Copia del libro de Excel renombrado
        .AddAttachment rutaCopiaExcel
        
        .Send
    End With

    ' ==========================================
    ' 7. ENVIAR NOTIFICACIÓN A GOOGLE CHAT WEBHOOK
    ' ==========================================
    If urlWebhook <> "" Then
        EnviarNotificacionWebhook urlWebhook, strFecha, nombreNuevoExcel, listaPara
    End If

    ' ==========================================
    ' 8. LIMPIEZA SILENCIOSA
    ' ==========================================
    On Error Resume Next
    Kill rutaImagen
    Kill rutaCopiaExcel
    On Error GoTo 0

    Application.CutCopyMode = False
    Set iMsg = Nothing
    Set iConf = Nothing
    Set Flds = Nothing

    ThisWorkbook.Save
End Sub

' =======================================================
' SUBRUTINA AUXILIAR PARA GOOGLE CHAT WEBHOOK
' =======================================================
Sub EnviarNotificacionWebhook(url As String, fechaReporte As String, archivo As String, destinatarios As String)
    On Error Resume Next
    Dim http As Object
    Dim jsonPayload As String
    
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    jsonPayload = "{" & _
        """text"": ""*REPORTE GENERADO Y ENVIADO EXITOSAMENTE*\n\n" & _
        "• *Fecha consulta:* " & fechaReporte & "\n" & _
        "• *Archivo adjunto:* " & archivo & "\n" & _
        "• *Destinatarios:* " & destinatarios & "\n" & _
        "• *Hora de ejecución:* " & Format(Now, "yyyy-mm-dd hh:mm:ss") & """" & _
    "}"
    
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json; charset=UTF-8"
    http.Send jsonPayload
    
    If http.Status <> 200 Then
        MsgBox "Error al enviar notificación a Google Chat: " & http.responseText, vbExclamation, "Webhook Error"
    End If
    
    Set http = Nothing
    On Error GoTo 0
End Sub

primero tiene que valdiar las tablas de aju ejecutar ele xel una vez que verifique que ya esta bien , entonces procede a enviar una prueba de correo a mi correo diego.sullcaray@confianza.pe entonces cuando le diga qu esta conforme el correo envie a los demas correo  con la cuenta mis como te pasesus cerdeniales 

corredor.sur02@confianza.pe
corredor.sur03@confianza.pe
corredor.sur04@confianza.pe
corredor.sur05@confianza.pe
corredor.sur06@confianza.pe
corredor.sur07@confianza.pe
corredor.sur08@confianza.pe
corredor.sur09@confianza.pe
corredor.sur10@confianza.pe
daniel.villavicencio@confianza.pe
david.vilcahuaman@confianza.pe
diego.arroyo@confianza.pe
elmer.tapia@confianza.pe
eny.avalos@confianza.pe
GERENTE-TERRITORIAL-gr@confianza.pe
gerentedecorredor.centrosur@confianza.pe
gerentedecorredor.limaoriente@confianza.pe
gerentedecorredor.norandino@confianza.pe
gerentes.decorredores@confianza.pe
gerentes-de-corredorgrupo@confianza.pe
gilmer.salvatierra@confianza.pe
henry.saldana@confianza.pe
juan.villacorta@confianza.pe
karroll.grajeda@confianza.pe
katerine.collazos@confianza.pe
Lideres-del-cambiogrupo@confianza.pe
mauro.ibanez@confianza.pe
michael.palacios@confianza.pe
nilda.quilla@confianza.pe
paul.dionisio@confianza.pe
ricardo.lazo@confianza.pe
sebastien.puertas@confianza.pe
seguimiento.comercialgrupo@confianza.pe
victor.blas@confianza.pe
yonder.huanis@confianza.pe
  
y en el de cmg-mora no peudo ejecutalo amnaulmnete 

