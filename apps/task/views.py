from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from apps.task.forms import TaskForm
from apps.task.models import Task
from django.utils import timezone


# Generic Views
def home(request):
    return render(request, 'home.html')

@login_required
def task(request):
    tasks = Task.objects.filter(user=request.user, date_complete__isnull=True)
    return render(request, 'task.html', {
        'tasks': tasks,
    })



#Task Completed List

@login_required
def task_completed_list(request):
    tasks = Task.objects.filter(user=request.user, date_complete__isnull=False).order_by('-date_complete')
    return render(request, 'task_completed_list.html', {
        'tasks': tasks,
    })



# User Creation
def user_signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm,
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'],
                )
                user.save()
                return redirect('login')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'User already exists'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Password do not match'
        })


# User Login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('task')
    else:
        if request.method == 'GET':
            return render(request, 'login.html', {
                'form': AuthenticationForm(),
            })
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('task')
            else:
                return render(request, 'login.html', {
                    'form': AuthenticationForm(),
                    'error': 'Username/password incorrect',
                })


# User Logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


# Task Creations
@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm,
        })
    else:
        form = TaskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('task')
        else:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Could not create task',
            })


# Task Detail

@login_required
def task_detail(request, task_id):
    task_det = get_object_or_404(Task, id=task_id, user=request.user)
    return render(request, 'task_detail.html', {
        'task': task_det,
    })



# Task Edit

@login_required
def task_edit(request, task_id):
    task_upt = get_object_or_404(Task, id=task_id, user=request.user)
    form = TaskForm(instance=task_upt)
    if request.method == 'GET':
        return render(request, 'task_update.html',{
            'form': form,
        })
    else:
        form = TaskForm(request.POST, instance=task_upt)
        if form.is_valid():
            form.save()
            return redirect('task')
        else:
            return render(request, 'task_update.html', {
                'form': form,
                'error': 'Could not update task',
            })

# Task Completed
@login_required
def task_completed(request, task_id):
    task_comp = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task_comp.date_complete = timezone.now()
        task_comp.save()
        return redirect('task')


@login_required
def task_delete(request, task_id):
    task_del = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task_del.delete()
        if task_del.date_complete:
            return redirect('task_completed_list')
        else:
            return redirect('task')
