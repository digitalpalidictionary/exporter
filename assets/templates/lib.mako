<%def name='google_link_dps(args, text)'>\
<%
    href = 'https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&' + '&'.join(args)
%>\
<a class="link" target="_blank" href="${href}"/>${text}</a>\
</%def>

<%def name='google_link_sbs(args, text)'>\
<%
    href = 'https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform?usp=pp_url&' + '&'.join(args)
%>\
<a class="link" target="_blank" href="${href}"/>${text}</a>\
</%def>
