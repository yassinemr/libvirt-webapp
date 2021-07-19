from django.urls import path

from .views import (
    addvolume,
    home,
    hostusage,
    instances,
    networks,
    network,
    preaddvolume,
    storages,
    storage,
    accesPage,
    logOut,
    preaddnetwork,
    addnetwork,
    rmvolume,
    preaddstorage,
    addstorage,

)

app_name='app'
urlpatterns = [
    path('',home,name='home'),
    path('vmachines',instances,name='vmachines'),
    path("hostusage", hostusage.as_view(), name="hostusage"),
    path("networks", networks, name="networks"),
    path("network/<str:pool>", network, name="network"),
    path("storages", storages, name="storages"),
    path("storage/<str:pool>", storage, name="storage"),
    path('login/',accesPage,name="login"),
    path('logout/',logOut,name="logout"),
    path("addnetworkForm/", preaddnetwork, name="addnetworkForm"),
    path("addnetwork/",addnetwork,name="addnetwork"),
    path('storage/<str:pool>/addvolume',addvolume,name='addvolume'),
    path('storage/<str:pool>/preaddvolume',preaddvolume,name='preaddvolume'),
    path('storage/<str:pool>/<str:name>',rmvolume,name='rmvolume'),
    path('preaddstorage',preaddstorage,name='preaddstorage'),
    path('addstorage',addstorage,name='addstorage'),
]