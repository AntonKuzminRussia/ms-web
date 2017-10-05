from django.conf.urls import url, include
from msw.views import mailbox, download, filters_finds, AddFilterForm, EditFilterForm, \
    AddAccountForm, EditAccountForm, accounts, attachments, attachments_list, index, del_filter, del_account, \
    accounts_errors
from msw.api import AccountsResource, FoldersResource, FiltersResource, \
    LettersResource, AttachmentsResource, FiltersFindsResource, FiltersFindsLettersResource, \
    SubjectsResource, AttachmentsListResource, StatsResource, AccountsErrorsResource
from tastypie.api import Api

#from rest_framework import routers
from msw import views

#router = routers.DefaultRouter()
#router.register(r'accounts', views.AccountsViewSet)
#router.register(r'folders', views.FoldersViewSet)

v1_api = Api(api_name='v1')
v1_api.register(AccountsResource())
v1_api.register(FoldersResource())
v1_api.register(FiltersResource())
v1_api.register(LettersResource())
v1_api.register(AttachmentsResource())
v1_api.register(FiltersFindsResource())
v1_api.register(FiltersFindsLettersResource())
v1_api.register(SubjectsResource())
v1_api.register(AttachmentsListResource())
v1_api.register(StatsResource())
v1_api.register(AccountsErrorsResource())
urls = [
    [
        #url(r'^folders/(?P<pk>\d+)/$', FoldersViewSet.as_view({'get': 'retrieve'}), name='user-detail'),
        #url(r'^folders/(?P<pk>\d+)/$', FoldersViewSet.as_view({'get': 'by_parent'}), name='user-detail'),
        url(r'^mailbox/$', mailbox, name="mailbox"),
        url(r'^index/$', index, name="index"),
        url(r'^accounts/$', accounts, name="accounts"),
        url(r'^accounts-errors/(?P<account_id>\d+)/$', accounts_errors, name="accounts-errors"),
        url(r'^attachments/$', attachments, name="attachments"),
        url(r'^attachments-list/(?P<ext>[a-z0-9]+)/$', attachments_list, name="attachments_list"),
        url(r'^filters-finds/$', filters_finds, name="filters-finds"),
        url(r'^add-filter/$', AddFilterForm.as_view(), name="add-filter"),
        url(r'^edit-filter/(?P<pk>[\w-]+)/$', EditFilterForm.as_view(), name="edit-filter"),
        url(r'^del-filter/(?P<id>\d+)/$', del_filter, name="del-filter"),
        url(r'^add-account/$', AddAccountForm.as_view(), name="add-account"),
        url(r'^del-account/(?P<id>\d+)/$', del_account, name="del-account"),
        url(r'^edit-account/(?P<pk>[\w-]+)/$', EditAccountForm.as_view(), name="edit-account"),
        url(r'^download/(?P<id>\d+)/$', download, name="download"),
        url(r'^api/', include(v1_api.urls)),

        #url(r'^', include(router.urls)),
        #url(r'^api-accounts/', include('rest_framework.urls', namespace='rest_framework'))
        # url(r'^api/', include(accounts_resource.urls)),
        # url(r'^api/', include(folders_resource.urls)),
        # url(r'^api/', include(filters_resource.urls)),
        # url(r'^api/', include(letters_resource.urls)),
        # url(r'^api/', include(accounts_resource.urls)),
        # url(r'^api/', include(attachments_resource.urls)),
        # url(r'^api/', include(filters_finds_resource.urls)),
    ],
    'msw',
    'msw',
]