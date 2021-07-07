from vrtManager.util import get_xml_path
from django.shortcuts import render,redirect
import sys
import libvirt
from hurry.filesize import size
from xml.dom import minidom
from django.template import RequestContext, context
from vrtManager.hostdetails import force_shutdown, get_cpu_usage, get_instance_managed_save_image, get_instance_memory, get_instance_status, get_instance_vcpu, get_ipv4_dhcp_range_end, get_ipv4_dhcp_range_start, get_ipv4_forward, get_ipv4_network, get_memory_usage, get_networks, get_networks_info, get_node_info, get_storages_info,hypervisor_type, managed_save_remove, managedsave, resume, shutdown, start, suspend
from libvirt import libvirtError
from django.http import HttpResponse, HttpResponseRedirect
import json
import time
from rest_framework.views import APIView 
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def accesPage(request):
    #######################
    
   # user = User.objects.create_user('kvmkvm', 'kvmkvm')
   # user.save()

    #######################
    #recuperation des donnees
    if request.method == "POST":
        nom=request.POST.get('username')
        passwd=request.POST.get('password')
        user=authenticate(request,username=nom,password=passwd)
        # si l'utilisateur est existe
        if user is not None:
            login(request,user)
            return redirect("/")
        else:
            messages.info(request,"username or password invalid !")
    context={}
    return render(request,'acces.html')

def logOut(request):
    logout(request)
    return redirect("/acces")

class hostusage(APIView):
    """
    Return Memory and CPU Usage
    """
    authentication_classes=[]
    permission_classes=[]

    def get(self,request,format=None):
        points = 10
        datasets = {}
        cookies = {}
        curent_time = time.strftime("%H:%M:%S")

        try:

            conn = libvirt.open('qemu:///system')
            cpu_usage = get_cpu_usage(conn)
            mem_usage = get_memory_usage(conn)

        except libvirtError:
            cpu_usage = 0
            mem_usage = 0

        try:

            cookies['cpu'] = request.COOKIES.get('cpu') 
            cookies['mem'] = request.COOKIES.get('mem') 
            cookies['timer'] = request.COOKIES.get('timer') 

        except KeyError:
            cookies['cpu'] = None
            cookies['mem'] = None

        if not cookies['cpu'] and not cookies['mem']:
            datasets['cpu'] = [0]
            datasets['mem'] = [0]
            datasets['timer'] = [curent_time]
        else:
            datasets['cpu'] = eval(cookies['cpu'])
            datasets['mem'] = eval(cookies['mem'])
            datasets['timer'] = eval(cookies['timer'])

        datasets['timer'].append(curent_time)
        datasets['cpu'].append(int(cpu_usage['usage']))
        datasets['mem'].append(int(-mem_usage['usage']) / 1048576)

        if len(datasets['timer']) > points:
            datasets['timer'].pop(0)
        if len(datasets['cpu']) > points:
            datasets['cpu'].pop(0)
        if len(datasets['mem']) > points:
            datasets['mem'].pop(0)

        data = json.dumps({'cpu': datasets['cpu'], 'mem': datasets['mem'],'timer': datasets['timer']})
   
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        response.cookies['cpu'] = datasets['cpu']
        response.cookies['timer'] = datasets['timer']
        response.cookies['mem'] = datasets['mem']
        response.write(data)
        return response

@login_required(login_url='/login')
def home(request):
    test = ""
    try:
        conn = libvirt.open('qemu:///system')

        if conn == None:
            test = 'Failed to open connection to qemu:///system' + str(file=sys.stderr)
        else:
            test = 'good'+' Connection is Alive: '+str(conn.isAlive())
            
    except:
        test = "dont have permissions"
    

    hostname, host_arch, host_memory, logical_cpu, model_cpu, uri_conn = get_node_info(conn)
    hypervisor = hypervisor_type(conn)
    mem_usage = get_memory_usage(conn)
    cpu_usage = get_cpu_usage(conn)
    network = get_networks_info(conn)
    print(network)
    
    
    context={
        'test':test,
        'hostname':hostname,
        'host_arch':host_arch,
        'host_memory':size(host_memory),
        'logical_cpu':logical_cpu,
        'model_cpu':model_cpu,
        'uri_conn':uri_conn,
        'hypervisor':hypervisor,
        }
        
    return render(request,"home.html",context)

@login_required(login_url='/login')
def instances(request):
    """
    Instances block
    """

    errors = []
    instances = []
    time_refresh = 8000
    get_instances = []
    conn = None

    test = ""
    try:
        conn = libvirt.open('qemu:///system')

        if conn == None:
            test = 'Failed to open connection to qemu:///system' + str(file=sys.stderr)
        else:
            test = 'good'+' Connection is Alive: '+str(conn.isAlive())
            
    except:
        test = "dont have permissions"

    get_instances = conn.listAllDomains(0)

    for instance in get_instances:
        name = instance.name()
        uuid=instance.UUIDString()
        instances.append({'name': name,
                          'status': get_instance_status(conn,name),
                          'uuid': uuid,
                          'memory': get_instance_memory(conn,name),
                          'vcpu': get_instance_vcpu(conn,name),
                          'has_managed_save_image': get_instance_managed_save_image(conn,name)})
    if conn:
        try:
            if request.method == 'POST':
                name = request.POST.get('name', '')
                if 'start' in request.POST:
                    start(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'shutdown' in request.POST:
                    shutdown(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'destroy' in request.POST:
                    force_shutdown(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'managedsave' in request.POST:
                    managedsave(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'deletesaveimage' in request.POST:
                    managed_save_remove(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'suspend' in request.POST:
                    suspend(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'resume' in request.POST:
                    resume(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
            conn.close()
        except libvirtError as err:
            errors.append(err)
    context={
       'instances': instances
    }

    return render(request,"vmachines.html",context)

"""network"""
@login_required(login_url='/login')
def networks(request):
    errors = []

    try:
        conn = libvirt.open('qemu:///system')
    
        networks = get_networks_info(conn)
        conn.close()
    except libvirtError as err:
        errors.append(err)

    context={
        'errors':errors,
        'networks':networks
    }
    return render(request,"networks.html",context)

@login_required(login_url='/login')
def network(request,pool):

    """
    Networks block
    """

    errors = []


    try:
        conn = libvirt.open('qemu:///system')
        network = conn.networkLookupByName(pool)
        state = network.isActive()
        device = network.bridgeName()
        autostart = network.autostart()
        ipv4_forward = get_ipv4_forward(network)
        ipv4_dhcp_range_start = get_ipv4_dhcp_range_start(network)
        ipv4_dhcp_range_end = get_ipv4_dhcp_range_end(network)
        ipv4_network = get_ipv4_network(network)
    except libvirtError as err:
        errors.append(err)
    
    if request.method == 'POST':
        if 'start' in request.POST:  
            network.create()
            return HttpResponseRedirect(request.get_full_path())
        if 'stop' in request.POST:
            network.destroy()
            return HttpResponseRedirect(request.get_full_path())
        if 'delete' in request.POST:
            network.undefine()
            return HttpResponseRedirect(request.get_full_path())
        if 'set_autostart' in request.POST:
            network.setAutostart(1)
            return HttpResponseRedirect(request.get_full_path())
        if 'unset_autostart' in request.POST:
            network.setAutostart(0)
            return HttpResponseRedirect(request.get_full_path())

    context={
        'network':network.name(),
        'state':state,
        'device':device,
        'autostart':autostart,
        'ipv4_forward':ipv4_forward,
        'ipv4_dhcp_range_start':ipv4_dhcp_range_start,
        'ipv4_dhcp_range_end':ipv4_dhcp_range_end,
        'ipv4_network':ipv4_network
    }

    print(context)
    return render(request,"network.html",context)

@login_required(login_url='/login')
def storage(request,pool):
    errors=[]

    try:
        conn = libvirt.open('qemu:///system')
        storage=conn.storagePoolLookupByName(pool)
        state = storage.isActive()
        size = storage.info()[1]
        free = storage.info()[3]
        used = size - free
        if state:
            percent = (used*100)//size
        else:
            percent = 0
        
        status = get_xml_path(storage.XMLDesc(0),"/pool/target/path")
        type = get_xml_path(storage.XMLDesc(0),"/pool/@type")
        autostart = storage.autostart()
        if request.method == 'POST':
            if 'start' in request.POST:
                try:
                    storage.create(0)
                    return HttpResponseRedirect(request.get_full_path())
                except libvirtError as error_msg:
                    errors.append(error_msg.message)
            if 'stop' in request.POST:
                try:
                    storage.destroy()
                    return HttpResponseRedirect(request.get_full_path())
                except libvirtError as error_msg:
                    errors.append(error_msg.message)
            if 'delete' in request.POST:
                try:
                    storage.delete()
                    return HttpResponseRedirect(reverse('storages'))
                except libvirtError as error_msg:
                    errors.append(error_msg.message)
            if 'set_autostart' in request.POST:
                try:
                    storage.setAutostart(1)
                    return HttpResponseRedirect(request.get_full_path())
                except libvirtError as error_msg:
                    errors.append(error_msg.message)
            if 'unset_autostart' in request.POST:
                try:
                    storage.setAutostart(0)
                    return HttpResponseRedirect(request.get_full_path())
                except libvirtError as error_msg:
                    errors.append(error_msg.message)
            conn.close()
    except libvirtError as err:
        errors.append(err)

    context={
        'pool':pool,
        'state':state,
        'size':size,
        'free':free,
        'used':used,
        'percent':percent,
        'status':status,
        'type':type,
        'autostart':autostart
    }

    return render(request,'storage.html',context)

@login_required(login_url='/login')
def storages(request):
    errors=[]

    try:
        conn = libvirt.open('qemu:///system')
        storages = get_storages_info(conn)
        conn.close()
    except libvirtError as err:
        errors.append(err)

    context={
        'storages':storages
    }

    return render(request,"storages.html",context)


