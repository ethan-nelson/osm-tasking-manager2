# -*- coding: utf-8 -*-
<%namespace file="custom.mako" name="custom"/>
<%namespace file="helpers.mako" name="helpers"/>
<%inherit file="base.mako"/>
<%block name="header">
</%block>
<%block name="content">
<%
base_url = request.route_path('home')
priorities = [_('urgent'), _('high'), _('medium'), _('low')]

sorts = [('priority', 'asc', _('High priority first')),
         ('created', 'desc', _('Creation date')),
         ('last_update', 'desc', _('Last update'))]
%>
<div class="container">
  <div class="col-md-6">
    <h3>What is the OSM Tasking Manager?</h3>
    <p>OSM Tasking Manager is a mapping tool designed and built for the Humanitarian OSM Team collaborative mapping. The purpose of the tool is to divide up a mapping job into smaller tasks that can be completed rapidly.</p>
    <p>Learn more</p>
    % if not user:
    <h4>Already have an account?</h4>
    <a class="btn btn-success" href="${request.route_path('login')}">Login</a> or <a href="http://www.openstreetmap.org/user/new">Create an account</a><br /><br />
    % endif
    <a href="${request.route_path('list')}">See all projects</a>
  </div>
  <div class="col-md-6">
    <div class="well well-sm">
      <center><h2>Learn to map!</h2>
      <img style="width: 300px;" src="http://i.imgur.com/9kdGWA4.png" /></center>
      <p>Visit the OSM wiki to learn about the Tasking Manger.</p>
      <p>LearnOSM will help you understand how to map.</p>
      <p>MapGive provides video tutorials about mapping.</p>
    </div>
  </div>
</div>
<% base_url = request.route_path('home') 
%>
<div class="container">
  <div class="col-md-4">
    % if well3 is not None and len(well3) != 0:
    <div class="well well-sm">
      <h3><a href="${base_url}list?search=tag%3A${front_tags[2]}">${front_tags[2]}</a></h3>
      % for project in well3:
        <a href="${base_url}project/${project.id}">#${project.id} ${project.name}</a><br />
      % endfor
      <hr />
      <a href="${base_url}list?search=tag%3A${front_tags[2]}">More projects</a>
    </div>
    % endif
  </div>
  <div class="col-md-4">
    % if well2 is not None and len(well2) != 0:
    <div class="well well-sm">
      <h3><a href="${base_url}list?search=tag%3A${front_tags[1]}">${front_tags[1]}</a></h3>
      % for project in well2:
        <a href="${base_url}project/${project.id}">#${project.id} ${project.name}</a><br />
      % endfor
      <hr />
      <a href="${base_url}list?search=tag%3A${front_tags[1]}">More projects</a>
    </div>
    % endif
  </div>
  <div class="col-md-4">
    % if well1 is not None and len(well1) != 0:
    <div class="well well-sm">
      <h3><a href="${base_url}list?search=tag%3A${front_tags[0]}">${front_tags[0]}</a></h3>
      % for project in well1:
        <a href="${base_url}project/${project.id}">#${project.id} ${project.name}</a><br />
      % endfor
      <hr />
      <a href="${base_url}list?search=tag%3A${front_tags[0]}">More projects</a>
    </div>
    % endif
  </div>
</div>
</%block>
