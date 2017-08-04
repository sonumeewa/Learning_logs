# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Topic, Entry
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from .forms import TopicForm, EntryForm

# Create your views here.
def index(request):
	"""render the home page for learning logs"""
	return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
	topics = Topic.objects.filter(owner=request.user).order_by('date_added')
	context = {'topics': topics}
	return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
	topic=Topic.objects.get(id= topic_id)
	# Make sure the topic belongs to the current user.

	if topic.owner != request.user:
		raise Http404

	entries = topic.entry_set.order_by('-date_added')
	context={'topic': topic, 'entries': entries}
	return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
	"""Add a new Topic."""
	if request.method != 'POST':
		form = TopicForm()
	else:
		"""Post data submitted, process data."""

		form = TopicForm(request.POST)
		if form.is_valid():
			new_topic = form.save(commit=False)
			new_topic.owner = request.user

			new_topic.save()
			return HttpResponseRedirect(reverse('learning_logs:topics'))
	context = {'form': form}
	return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
	"""Add a new entry for a particular topic."""
	topic=Topic.objects.get(id=topic_id)
	if request.method != 'POST':
		#NO DATA SUBMITTED CREATE BLANK FORM.
		form= EntryForm()
	else:
		#Post datasubmitted ; process data
		form = EntryForm(data = request.POST)
		if form.is_valid():
			if topic.owner ==request.user:
				new_entry = form.save(commit = False)
				new_entry.topic = topic
				new_entry.save()
				return HttpResponseRedirect(reverse('learning_logs:topic', args = [topic_id]))
			else:
				raise Http404
	context = {'topic':topic, 'form':form}
	return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
	"""edit an existing entry."""
	entry = Entry.objects.get(id= entry_id)
	topic = entry.topic
	# Make sure the topic belongs to the current user.

	if topic.owner != request.user:
		raise Http404
	if request.method != 'POST':
		# Initial request; pre-fill form with the current entry.
		form = EntryForm(instance=entry)
	else:
		# POST data submitted; process data.
		form = EntryForm(instance=entry, data=request.POST)
	if form.is_valid():
		form.save()
		return HttpResponseRedirect(reverse('learning_logs:topic',args=[topic.id]))
	context = {'entry': entry, 'topic': topic, 'form': form}
	return render(request, 'learning_logs/edit_entry.html', context)
