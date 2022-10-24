<%def name='google_href_dps(args, text)'>\
<%
    href = 'https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&' + '&'.join(args)
%>\
<a class="link" target="_blank" href="${href}"/>${text}</a>\
</%def>
