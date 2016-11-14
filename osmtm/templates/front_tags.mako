<%inherit file="base.mako"/>
<%block name="content">
<div class="container">
Select the tags you would like to display on the front page (up to 3--if you do more, unpredictable things will happen):
<form method="post" action="" class="form-horizontal">
  % for tag in tags:
    <% checked = '' %>
    % for front_tag in front_tags:
      % if front_tag.tag == tag.id:
        <% checked = 'checked' %>
      % endif
    % endfor
    <input type="checkbox" ${checked} id="tag_${tag.id}" name="tag_${tag.id}"></input> ${tag.name}</p>
  % endfor
<input id="submit" type="submit" value="${_('Save new front page projects')}" name="form.submitted" class="btn btn-primary"/>
</form>
</div>
</%block>
