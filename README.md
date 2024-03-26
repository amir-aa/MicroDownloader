# MicroDownloader
This service can handle download tasks and show the progress percent. download is available in two forms:<br />
1.Normal Download (Method :download_file_with_progress)<br />
2.Limited Download (Method :download_file_with_progress_limited)<br />
 Limit is defined hardcoded as LIMIT constant(default 0.5MBps)<br />
 Limiter is really simple. it makes an interrupt to regulate the maximum bytes should be downloaded every minute.
 for more accuracy you can do it every 10seconds or even 1 second
This app generates ID for each Download task and start a new thread!<br />
/download & /limitdownload are main endpoints to make a download task<br />
/selectall in the end point you can see all downlowd tasks<br />
/progress/<ActionID> can indicate progress percent 
 
