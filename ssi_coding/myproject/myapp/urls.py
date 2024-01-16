from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('select/', views.select_page, name='select_page'),

    path('select/user', views.service_user, name='service_user'),

    path('select/user/sk', views.gen_sk, name='gen_sk'),
    path('select/user/sk/imageprocess', views.image_process, name='img_proc'),

    path('select/user/sk/recovery', views.recovery_sk, name='recover_sk'),
    path('select/user/sk/recovery/process', views.recovery_process, name='recovery_process'),

    path('select/user/genvc', views.gen_vc, name='gen_vc'),
    path('select/user/genvc/process', views.vc_process, name='vc_process'),

    path('select/user/manvc', views.manage_vc, name='manage_vc'),
    path('select/user/manvc/getCmscInfo', views.get_cmsc_info, name='get_cmsc_info'),
    path('select/user/manvc/modifyCmscInfo', views.modify_cmsc_info, name='modify_cmsc_info'),
    path('select/user/manvc/changeAccessCmsc', views.change_access_cmsc, name='change_access_cmsc'),
    path('select/user/manvc/changeAccessor', views.change_accessor, name='change_accessor'),
    path('select/user/manvc/changeCmscKeyOwner', views.change_cmsc_key_owner, name='change_cmsc_key_owner'),

    path('select/user/manvc/getVcInfo', views.get_vc_info, name='get_vc_info'),
    path('select/user/manvc/getVcInfoAll', views.get_vc_info_all, name="get_vc_info_all"),
    path('select/user/manvc/modifyClaimInfo', views.modify_claim_info, name="modify_claim_info"),
    path('select/user/manvc/getVcRevocationList', views.get_vc_revocation_list, name="get_vc_revocation_list"),
    path('select/user/manvc/vcRevoke', views.vc_revoke, name="vc_revoke"),
    path('select/user/manvc/changeVccscKeyOwner', views.change_vc_key_owner, name='change_vc_key_owner'),
    path('select/user/manvc/addNewVC', views.add_vc, name='add_vc'),
    path('select/user/manvc/addNewClaim', views.add_new_claim, name='add_new_claim'),

    path('select/sp', views.service_provider, name='service_provider'),
    path('select/sp/verify', views.user_verify, name='service_verify')

]

