from __future__ import unicode_literals

import sendgrid
import os
from sendgrid.helpers.mail import *

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Post, Comment, Category, PostPreferrence, ReplyToComment,Cluster, Resource
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm, ContactForm, SearchForm, ReplyToCommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from ipware import get_client_ip
from django.template import Context
import re, random
from django.db.models import Q
from django.contrib import messages
from django.db.models import Count
from users.models import CustomUser, UserProfile
from users.forms import CustomUserCreationForm, UserProfileForm
from enpApi.models import PlaySession, Player
from django.template.loader import render_to_string
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied

from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from .suggestions import update_clusters

import pygal
from .chart import CatPieChart, PollHorizontalBarChart
from django.views.generic import TemplateView

from django.contrib.auth.models import User, auth



def index(request):
    print("<index>")
    context = {}
    if request.method == 'GET':
        print("\trequest.method == GET")
        form = ContactForm()
        return render(request, 'blog/home.html', {'form' : form})
    return render(request, 'blog/home.html', context)


def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )


# Create your views here.
def login_portal(request):
    print('======== LOGIN PORTAL (login_portal) ========')
    
    print(request.method)

    if request.method == 'POST':
        print('WORKING?')
    else:
        print('error')

    context = {}
    return render(request, 'blog/login_portal.html', context)
    # return redirect('portal/home.html')


def modules(request):
    if request.user.is_authenticated:
        return render(request, 'blog/modules.html')
    else:
        return render(request, 'blog/login_portal.html')


def modules_s(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        context = { 'player': player }
        return render(request, 'blog/modules_s.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def downloads(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        context = { 'player': player }
        return render(request, 'blog/downloads.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def downloads_s(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        context = { 'player': player }
        return render(request, 'blog/downloads_s.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def reg_from_invite(request):
    if request.method == 'GET':
        code = request.GET['code']
        try:
            invite = Invite.objects.get(link=code)
            email = invite.email
            employer = invite.employer
            print (username)
        except ObjectDoesNotExist:
            print("Not found")
    return render(request, 'blog/reg_from_invite.html')


def register_new_employee(request):
    return render(request, 'blog/modules.html')


def employee_reg(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        context = { 'player': player }
        return render(request, 'blog/employee_registration.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def send_reg(request):
    return render(request, 'blog/login_portal.html')
    

def employee_progress(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        player = Player.objects.get(user=request.user)
        print (player.user.username)
        
        context = { 'player': player }
        return render(request, 'blog/employee_progress.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def nonsupervisor_progress(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        user_email = request.user.email
        players = Player.objects.filter(employer='0').filter(supervisor='False')
        #print (sessions.count)
        context = { 'players': players, 'player': player }
        return render(request, 'blog/nonsupervisor_progress.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def supervisor_progress(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        user_email = request.user.email
        players = Player.objects.filter(employer='0').filter(supervisor='True')
        #print (sessions.count)
        context = { 'players': players, 'player': player }
        return render(request, 'blog/supervisor_progress.html', context)
    else:
        return render(request, 'blog/login_portal.html')


def attempt_login(request):
    if request.method == 'GET':
        employee_user = request.GET['user']
        employee_password = request.GET['pass']
        user = authenticate(username=employee_user, password=employee_password)
        if user is not None:
            data = { 'valid': 'yes', 'email': user.email }
            return JsonResponse(data)
        else:
            data = { 'valid': 'no' }
            return JsonResponse(data)
    if request.method == 'POST':
        employee_user = request.POST.get("user")
        print(employee_user)
        employee_pass = request.POST.get("pass")
        print(employee_pass)
        user = authenticate(username=employee_user, password=employee_pass)
        if user is not None:
            data = { 'valid': 'yes', 'email': user.email }
            return JsonResponse(data)
        else:
            data = { 'valid': 'no' }
            return JsonResponse(data)


#
# Global variables across all templates
# 
def category(request):
  categories = Category.__members__.items()
  user_ip = get_client_ip(request)
  ip = user_ip[0]
  
  request.session['ip'] = ip
  
  if request.user.is_authenticated: 
    user = CustomUser.objects.get(pk=request.user.pk)
    user_form = UserProfileForm(instance=user)

    ProfileInlineFormset = inlineformset_factory(CustomUser, UserProfile, fields=('photo',))
    formset = ProfileInlineFormset(instance=user)

    if request.user.id == user.id:
        if request.method == "POST":
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)
            
    return {
        'categories' : categories,
        'signup_form': CustomUserCreationForm(),
        'isLoggedIn': True,
        'userprofile': formset,
    }
  else :
    return {
        'categories' : categories,
        'signup_form': CustomUserCreationForm(),
        'isLoggedIn': False,
    }
        
# Popular cases
# list top 3 cases with the most comments
# get no. of comments for all posts
def popular_cases(request):
  cases = Comment.objects.filter(approved_comment=True).values('post').annotate(dcount=Count('post')).order_by('-dcount')
  default_cases = []
  
  if not cases.first():
    default_cases = Post.objects.filter(pk__in=[1, 2, 3])
  else:
    default_cases = []
    
  size = Post.objects.all().count();
  
  count = 0;
  pop_posts = [];
  casesparsed = {};
  
  for case in cases:
    casesparsed[case['post']] = case['dcount']
    
    if count < 3:
      #print(case['post'])
      #print(Post.objects.filter(pk=case['post']))
      pop_posts.append(Post.objects.filter(pk=case['post']))
      count = count + 1;
  
  #print(casesparsed)
  random_cases = []
  limit = len(Post.objects.all())
  if limit > 2:
    random_numbers = random.sample(range(1, limit), 2)
  elif limit > 1:
    random_numbers = [1, 2]
  elif limit > 0:
    random_numbers = [1]
  else:
    random_numbers = []
  random_cases = Post.objects.filter(pk__in=random_numbers)  
  
  return {'pop_cases' : pop_posts, 
          'cases':casesparsed, 
          'random_cases': random_cases,
          'default_cases' : default_cases}

# Recommendation
def user_recommendation_list(request):
  post_list = {}
  
  if request.user.is_authenticated:
    # get the user commented:
    user_commented = Comment.objects.filter(author=request.user.username).prefetch_related('post')
    user_metooed = PostPreferrence.objects.filter(vote_value=1, username=auth.get_user(request))
    
    user_commented_posts = set(map(lambda x: x.post.pk, user_commented))
    user_metooed_posts = set(map(lambda x: x.postpk.pk, user_metooed))
    
    #print (user_commented_posts)
    #print (user_metooed_posts)
    
    # the set of posts this user commented and metooed
    user_set = user_commented_posts | user_metooed_posts
    #print (recommend_set)
    
    #get user cluster name & get all other cluster members
    try:
       user_cluster = CustomUser.objects.get(username=auth.get_user(request)).cluster_set.first().name
    
    except: # if no cluster assigned for a user, update clusters
       update_clusters("true")
       user_cluster = CustomUser.objects.get(username=auth.get_user(request)).cluster_set.first().name
    
    user_cluster_other_members = Cluster.objects.get(name=user_cluster).users.exclude(username=auth.get_user(request)).all()
    other_members_usernames = set(map(lambda x: x.username, user_cluster_other_members))
    
    # get other users' commented and metooed posts from the same clusters
    other_user_commented_posts = Comment.objects.filter(author__in=other_members_usernames).exclude(post__pk__in=user_set)
    other_user_metooed_posts =  PostPreferrence.objects.filter(username__username__exact=other_members_usernames, vote_value=1).exclude(postpk__pk__in=user_set)        
    
    other_user_commented = set(map(lambda x: x.post.pk, other_user_commented_posts))
    other_user_metooed = set(map(lambda x: x.postpk.pk, other_user_metooed_posts))
    
    other_users_set = other_user_commented | other_user_metooed
    
    post_list_1 = list(Post.objects.filter(id__in=other_users_set))
    post_list_2 = list(Post.objects.exclude(id__in=user_set))
    
    post_list = list(set(post_list_1)|set(post_list_2))[:3]
    
    #print(post_list)
    #print(other_users_set)
    #print(other_members_usernames)
  
  return {'rec_post_list': post_list}

#
# For About us page
#
def about_sisu(request):
    context = {
        'signup_form': CustomUserCreationForm()
    }
    
    return render(request, 'blog/about.html', context)
    
def about_us(request):
    return render(request, 'blog/about_us.html')
    
def about_team(request):
    return render(request, 'blog/about_team.html')    

def about_program(request):
    return render(request, 'blog/about_program.html')    

def terms_conditions(request):
    return render(request, 'blog/terms_condition.html')
    
def privacy_policy(request):
    return render(request, 'blog/privacy_policy.html')

def header(request):
    return render(request, 'blog/header.html')


# Training Portal Authentication / Login, Logout - START
def portal_login(request):
    # todo - better method is to incorporate 'next=?' operations and logic
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/portal/home/')
        else:
            context = {'bad_login_is': True}
            messages.info(request, 'invalid credentials')
            # messages.info(request, 'invalid credentials')
            return render(request, 'auth/login.html', context)
    else:    
        return render(request, 'auth/login.html')
    
    return render(request, 'auth/login.html')
    

def portal_logout(request):
    auth.logout(request)
    return redirect('/')


def key_redeem(request):
    context = {'key': '1111-2222-3333-4444'}
    return render(request, 'auth/key-redeem.html', context)

# Training Portal Authentication / Login, Logout - END




# Training Portal - START
def portal_home(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        play_sessions = PlaySession.objects.filter(player=str(player)).order_by('module_id')
        play_sessions_completed = PlaySession.objects.filter(player=str(player)).filter(success=True)

        context = {'player': player, 'play_sessions': play_sessions, 'play_sessions_completed': play_sessions_completed}
    
        return render(request, 'portal/home.html', context)
    else:
        return render(request, 'auth/login.html')


def portal_register(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)

        context = {'player': player}
        
        if request.method == 'POST':
            print('---- PORTAL_REGISTER - POST.REQUEST ----') 
            # vr | non-supervisor and supervisor
            emails_vr_nonsupervisor = request.POST['vr-nonsupervisor']
            emails_vr_supervisor = request.POST['vr-supervisor']
            # desktop | non-supervisor and supervisor            
            emails_desktop_nonsupervisor = request.POST['desktop-nonsupervisor']
            emails_desktop_supervisor = request.POST['desktop-supervisor']

            print('emails_vr_nonsupervisor = {}'.format(emails_vr_nonsupervisor))
            print('emails_vr_supervisor = {}'.format(emails_vr_supervisor))
            print('emails_desktop_nonsupervisor = {}'.format(emails_desktop_nonsupervisor))
            print('emails_desktop_supervisor = {}'.format(emails_desktop_supervisor))

        return render(request, 'portal/register.html', context)
    else:
        return render(request, 'auth/login.html')


def portal_edit_registration(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        players = Player.objects.filter(employer=player.employer)

        context = {'player': player, 'players': players}
        
        return render(request, 'portal/edit-registration.html', context)
    else:
        return render(request, 'auth/login.html')
        

def portal_training_dl(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        context = {'player': player}
        return render(request, 'portal/downloads.html', context)
    else:
        return render(request, 'auth/login.html')


def portal_employee_progress(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        players = Player.objects.filter(employer=player.employer)
        play_sessions = PlaySession.objects.filter(employer=player.employer)

        players_obj = []

        # creating dictionary with aggregated data to be rendered to DOM.
        # reason for doing this is because quantity of modules completed player are from two different data sets and require looping
        for i, player_single in enumerate(players):
            if player_single.supervisor == True: registration_type = 'Supervisor' 
            else: registration_type = 'Non-supervisor'

            players_obj.append({
                'name': player_single.full_name,
                'email': player_single.email,
                'registration': registration_type,
                'modules_completed': len(PlaySession.objects.filter(employer=player.employer).filter(player=player_single).filter(success=True))
            })

        
        context = {'player': player, 'players': players, 'play_sessions': play_sessions, 'players_obj': players_obj}
        
        return render(request, 'portal/progress.html', context)
    else:
        return render(request, 'auth/login.html')


def portal_settings(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        context = { 'player': player }
        return render(request, 'portal/settings.html', context)
    else:
        return render(request, 'auth/login.html')


def portal_certificate(request):
    if request.user.is_authenticated:
        player = Player.objects.get(user=request.user)
        play_sessions = PlaySession.objects.filter(player=str(player)).order_by('module_id')
        play_sessions_completed = PlaySession.objects.filter(player=str(player)).filter(success=True)

        context = {'player': player, 'play_sessions': play_sessions, 'play_sessions_completed': play_sessions_completed}
    
        return render(request, 'portal/certificate.html', context)
    else:
        return render(request, 'auth/login.html')

# Training Portal - END



def story(request, category_name):
    # print(pretty_request(request))
    posts = Post.objects.filter(category_name=category_name).order_by('-published_date')
    cat = Category.get_label(category_name)   
    mapping = {}
  
    # Bad hard codes...
    mapping[Category.Harassment] = "An unpleasant or hostile situation created by uninvited and unwelcome verbal or physical conduct"
    mapping[Category.Discrimination] = "The unjust or prejudicial treatment of different categories of persons, especially on the grounds of race, age, or sex"
    mapping[Category.Politics] = "Devious or divisive activity aimed at improving the status of one or more persons in an organization"
    mapping[Category.Conflict] = "A serious disagreement or argument between persons of similar age, status, or abilities"
    mapping[Category.Miscellaneous] = "Additional cases which do not fall under a particular category"   
    return render(request, 'blog/story.html', {'posts':posts, 'cat':cat, 'description': mapping[cat]})
    

def get_all_category(request):
    return render(request, 'blog/story_cat_main.html')    

   
def story_entry(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user_name = auth.get_user(request)
    ip = request.session['ip']
    
    hit_count = HitCount.objects.get_for_object(post)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)    
    
    #print ("hit---- " + str(hit_count_response.hit_message))
    
    # Get resources
    random_num = []
    random_res = []
    res = Resource.objects.filter(category_name=post.category_name)
    random_num = list(map(lambda x: x.pk, res))
    
    limit = len(res)
    
    if limit > 2:
        random.shuffle(random_num)
        random_num = random_num[:3]
        
    if(random_num): 
        random_res = Resource.objects.filter(pk__in=random_num)
        
    #print(random_num)
    
    if request.user.is_authenticated:
        if PostPreferrence.objects.filter(username=user_name, ip_address=ip, postpk=pk, vote_value=1).exists():   
            voted = True
        else:
            voted = False
        
    else:
        if PostPreferrence.objects.filter(ip_address=ip, postpk=pk, vote_value=1).exists(): 
            voted = True
        else:
            voted = False   
    try:
        total_yes = PostPreferrence.objects.filter(vote_value=1, postpk=pk).count()
    except PostPreferrence.DoesNotExist:
        total_yes = 0;
        
    
    summary = ({
        'voted':voted,
        'total_yes': total_yes,

    }) 
    
    return render(request, 'blog/story_entry.html', 
                  {'post': post, 
                   'summary': summary,
                   'resources': random_res,
                  })    


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    
    return render(request, 'blog/post_list.html', {'posts':posts})
    
# Post.objects.get(pk=pk)
def post_cases(request):
    return render(request, 'blog/post_category_main.html')
    
def post_list_by_category(request, category_name):
    posts = Post.objects.filter(category_name=category_name).order_by('-published_date')
    cat = Category.get_label(category_name)
    return render(request, 'blog/post_list.html', {'posts':posts, 'cat':cat })
   
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required   
def post_draft_list(request):
  posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
  return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required  
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish_post()
    return redirect('post_detail', pk=pk)

@login_required    
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

@login_required     
def post_edit(request, pk):

    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required     
def add_comment_to_post(request):
  
  if request.method == "GET":
     pid = request.GET['pid']
     author = request.GET['author']
     content = request.GET['text']
     
     commentpost = get_object_or_404(Post, pk=pid)
     
     comment = Comment()
     comment.post = commentpost
     comment.author = author
     comment.user = request.user
     
     userprofile = get_object_or_404(UserProfile, user=comment.user)
     comment.userprofile = userprofile
     
     comment.text = content
     
     comment.save()
    
     update_clusters("false")
           
  else:
     form = CommentForm()
    
  return render(request, 'blog/story_entry.html', {'post':commentpost})    
    
@login_required     
def add_reply_to_comment(request):
    
    if request.method == "GET":
        pid = request.GET['pid']
        cid = request.GET['cid']
        author = request.GET['author']
        content = request.GET['text']
        
        replypost = get_object_or_404(Post, pk=pid)
        comment = get_object_or_404(Comment, post=replypost, pk=cid)
        
        replyToComment = ReplyToComment()
        replyToComment.post = replypost
        replyToComment.comment = comment
        replyToComment.author = author
        replyToComment.text = content
        replyToComment.user = request.user
     
        userprofile = get_object_or_404(UserProfile, user=replyToComment.user)
        replyToComment.userprofile = userprofile
        
        replyToComment.save()
           
        data = {
            'success': True,
            'newReply': replyToComment.created_date
        }
    else:
        form = CommentForm()
    return JsonResponse(data)
    #return render(request, 'blog/story_entry.html', {'post':replypost})
    
@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('story_entry', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('story_entry', pk=comment.post.pk)
#
# For contact us page
#
def contact_us(request):
    print( "Inside contact_us block")
    if request.method == 'GET':
        print("Registering as GET")
        form = ContactForm()
    else:
        print("Registering as POST")
        form = ContactForm(request.POST)
        if form.is_valid():
            print("Form is valid");
            sender = "From " + form.cleaned_data['your_name']
            if request.user.is_authenticated:
              sender = sender + "_(REG_User)_" + auth.get_user(request).username
            else:
              sender = sender + "_(PUB_User)_"
              
            print (os.environ.get('SENDGRID_API_KEY'))  
            sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            print("Set sendgrid instance")
            from_email = Email(form.cleaned_data['your_email'])
            print("Set from email")
            to_email = Email("Hello@sisuvr.com")
            print("Set to email")
            company = sender + form.cleaned_data['your_company']
            #company = form.cleaned_data['your_company']
            print("Set company")
            subject = company + form.cleaned_data['subject']
            #subject = sender + form.cleaned_data['subject']
            print("Set subject")
            content = Content("text/plain", form.cleaned_data['message'])
            print("Creating mail structure")
            mail = Mail(from_email, subject, to_email, content)
            print("Attempting to send mail")
            response = sg.client.mail.send.post(request_body=mail.get())
            '''print(response.status_code)
            print(response.body)
            print(response.headers) 
            '''
            '''
            from_email = form.cleaned_data['your_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
                '''
            # return render(request, 'blog/contact_us_success.html')
            print("Sent mail!")
            context = {}
            return render(request, 'blog/home.html', context)
        print("Form is invalid")
    return render(request, "blog/contact_us.html", {'form': form})
           
   
def on_off_star(request):

   if request.method == 'GET':
      post_id = request.GET['postid']
      post_preference = request.GET['on_off_value']
      user_name = auth.get_user(request)
      ip = request.session['ip']
      likedpost = get_object_or_404(Post, pk=post_id)
   
      voted = True
      try:
        if request.user.is_authenticated:
          postpreferrence_obj = PostPreferrence.objects.get(username=user_name, postpk=likedpost, ip_address=ip)     
        else:
          postpreferrence_obj = PostPreferrence.objects.get(postpk=likedpost, ip_address=ip)
        
        postpreferrence_obj.vote_value = post_preference
        postpreferrence_obj.save()    
                
        
      except PostPreferrence.DoesNotExist:
        post_voted = PostPreferrence()
        post_voted.ip_address = ip
        post_voted.postpk = likedpost
        post_voted.vote_value = post_preference 
      
        if request.user.is_authenticated:
          #print("===================================" + str(user_preference) + str(ip) + str(user_name))
          post_voted.username = user_name
        else:
          post_voted.username = None
          
        post_voted.save()   
        voted = True
   
      summary = ({
         'voted':voted,
         'total_yes': PostPreferrence.objects.filter(vote_value=1, postpk=post_id).count(),
      })
      
      update_clusters("false")
      
   return render(request, 'blog/story_entry.html', {'post':likedpost, 'summary':summary})   
   #return render(request, 'blog/post_detail_index.html', {'post':likedpost, 'summary':summary})   
 
# Search Functionality
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
 
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
    
def search(request):
    query_string = ''
    found_entries = None
    
    if request.method == "POST":
       search_form = SearchForm(request.POST)
      
       if search_form.is_valid():
          query_string = search_form.cleaned_data['search_string']
          post_query = get_query(query_string, ['title', 'text', 'category_name'])
          found_entries = Post.objects.filter(post_query).order_by('-published_date')
            
    else:
       search_form = SearchForm()
    
    return render(request, 'blog/post_search_res.html',{ 'query_string': query_string, 'found_entries': found_entries })
###

#
# For User Settings
#
@login_required
def user_profile(request, pk):
    user = CustomUser.objects.get(pk=pk)
    user_form = UserProfileForm(instance=user)

    ProfileInlineFormset = inlineformset_factory(CustomUser, UserProfile, fields=('photo',))
    formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserProfileForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return render(request, "blog/user_settings_profile_upd.html")
            
            
        return render(request, "blog/user_settings.html", {
            "noodle": pk,
            "noodle_form": user_form,
            "formset": formset,
        })
    else:
        raise PermissionDenied
    #return render(request, 'blog/user_settings.html')

@login_required
def user_details(request, pk):
    user = CustomUser.objects.get(pk=pk)
    user_form = UserProfileForm(instance=user)

    ProfileInlineFormset = inlineformset_factory(CustomUser, UserProfile, fields=('photo',))
    formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserProfileForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return render(request, "blog/user_settings_profile_upd.html")
            
            
        return render(request, "blog/user_details.html", {
            "noodle": pk,
            "noodle_form": user_form,
            "formset": formset,
        })
    else:
        raise PermissionDenied

def user_edit(request, pk): 

    return render(request, "blog/user_edit.html", { 'isValid': True })

## Pie chart
class IndexView(TemplateView):
      template_name = 'blog/user_details.html'
      
      def get_context_data(self, **kwargs):
          context = super(IndexView, self).get_context_data(**kwargs)
          user = self.request.user
          
          user_comments_approve = Comment.objects.filter(approved_comment=True, author=user).order_by('-created_date')
          user_comments_pending = Comment.objects.filter(approved_comment=False, author=user).order_by('-created_date')
          user_metooed = PostPreferrence.objects.filter(vote_value=1, username=user).order_by('-vote_date')
    
          user_comments = user_comments_approve | user_comments_pending
          
          # Get user profile info
          cus_user = CustomUser.objects.get(pk=user.pk)
          user_form = UserProfileForm(instance=cus_user)

          ProfileInlineFormset = inlineformset_factory(CustomUser, UserProfile, fields=('photo',))
          formset = ProfileInlineFormset(instance=cus_user)
          
          user_data = []
          for comment in user_comments:
            user_data.append(comment.post)
          
          for metoo in user_metooed:
            user_data.append(metoo.postpk)
          
          if len(user_data) != 0:
            cat_chart = CatPieChart(
                          height = 600,
                          width = 800,
                          explicit_size=True,
                          )
                          
            context['cat_chart'] = cat_chart.generate(user_data)
          
          else:
            context['cat_chart'] = None
          
          context['user_commented_size'] = len(user_comments_approve)
          context['user_pending_size'] = len(user_comments_pending)
          context['user_metooed_size'] = len(user_metooed)
          context['user_commented'] = user_comments_approve[:20]
          context['user_pending'] = user_comments_pending[:20]
          context['user_metooed'] = user_metooed
          context['noodle_form'] = user_form
          context['formset'] = formset
          
          return context