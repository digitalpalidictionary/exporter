<%def name='_google_link(base_href, entry, text, args=[])'>\
<%
    from datetime import date
    args_str = f'usp=pp_url&entry.438735500={entry}&entry.1433863141=GoldenDict%20{date.today()}' + '&'.join(args)
    href = f'{base_href}?{args_str}'
%>\
<a class="link" target="_blank" href="${href}"/>${text}</a>\
</%def>

<%def name='google_link_dps(entry, text, args=[])'>\
${_google_link('https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform', entry, text, args)}\
</%def>

<%def name='google_link_sbs(entry, text, args=[])'>\
${_google_link('https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform', entry, text, args)}\
</%def>

<%def name='today()'>\
<%
    from datetime import date
%>
${date.today()}
</%def>
