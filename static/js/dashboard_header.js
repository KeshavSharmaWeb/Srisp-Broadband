window.onload = (function () {
		if (!!window.EventSource) {
			var source = new EventSource("controller/dashboard.php?action=dashboard_header");
			//var source = new EventSource(location.origin + location.pathname + (location.search || '?') + '&data');

			source.addEventListener("message", function(e) {
				var result = JSON.parse(e.data);
				var remain_data = result.remain_data;
				var remain_uptime = result.remain_uptime;
				var remain_days = result.remain_days;
				var today_usage = result.today_usage;

				var conn_status = 'Offline';
				var conn_symbol = 'text-danger';

				if(result.online_user > 0 && result.online_user != "")
				{
					conn_status = 'Online ('+ result.online_user + ')';
					conn_symbol = 'text-success';
				}

				$('#remain_data').html(remain_data);
				$('#remain_uptime').html(remain_uptime);
				$('#remain_days').html(remain_days);
				$('#today_usage').html(today_usage);

				$('#conn_symbol').removeClass('text-danger');
				$('#conn_symbol').removeClass('text-success');
				$('#conn_symbol').addClass('fa fa-circle');
				$('#conn_symbol').addClass(conn_symbol);
				$('#conn_status').html(conn_status);


                        
                        
				
			}, false);
			
			source.addEventListener("open", function(e) {
				//logMessage("OPENED");
			}, false);

			source.addEventListener("error", function(e) {
				//logMessage("ERROR");
				if (e.readyState == EventSource.CLOSED) {
					//logMessage("CLOSED");
				}
			}, false);
		} else {
			// document.getElementById("notSupported").style.display = "block";
		}
	})();