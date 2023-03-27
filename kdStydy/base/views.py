from django.shortcuts import render ,redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Room , Topic ,Message
from django.http import HttpResponse
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout 
from django.contrib import messages 
from django.contrib.auth.forms import UserCreationForm

# rooms = [
#     {'id':1 , 'name':'Python'},
#     {'id':2 , 'name':'Go'},
#     {'id':3 , 'name':'Java'},

# ]

def loginPage(request):
    page = 'login'

    if request.method == 'POST':
        username= request.POST.get('username').lower()
        password= request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else :
            messages.error(request, 'Username or Password does not exist')



    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    

def registerPage(request):
    form = UserCreationForm()
    if request.method== 'POST':
        
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
          
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')


    return render(request, 'base/login_register.html',{'form': form})


def home (request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)

    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))


    context = {'rooms': rooms , 'topics' : topics, 
        'room_count' : room_count , 'room_messages' : room_messages }
    return render(request,'base/home.html',context)

def room (request,pk):
    room =Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    

    if request.method == 'POST':
        message =Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        return redirect('room', pk=room.id)

    context = {'room': room ,'room_messages' : room_messages,'participants': participants}
    return  render(request,'base/room.html',context)


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages  = user.message_set.all()
    topics = Topic.objects.all()

    context={'user':user, 'rooms':rooms ,
        'room_messages':room_messages, 'topics':topics
    }
    return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home' )


    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('your not allowed here')


    if request.method == 'POST':
        form = RoomForm(request.POST ,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context= {'form': form}
    return render(request, 'base/room_form.html',context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': message})