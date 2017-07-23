	</div> <!-- .container -->

	<script src="/static/jquery-3.2.1.js"></script>
	<script src="/static/bootstrap-3.3.7/js/bootstrap.js"></script>
	<script src="/static/validator.js"></script>
	<%
	if get("scripts"):
		for script in scripts:
	%>
	<script src="{{script}}"></script>
	<%
		end
	end
	%>
	
</body>
</html>
