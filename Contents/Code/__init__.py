
VIDEO_PREFIX = "/video/yousee"
#MUISC_PREFIX = "/music/yousee"
import datetime


NAME = L('Title')

ART  = 'art-default.jpg'
ICON = 'icon-default.png'
LIVE_SOURCE_URL = "http://yousee.tv/feeds/player/livetv/%s"
APPKEY = 'Plex'
APIKEY = 'qUkcfVVjosq3910c6LSN6pBg0O2XTyjz8kiwUc3L'
APIURL = 'http://api.yousee.tv/rest/'


####################################################################################################

def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = ART
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
#    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13"
    HTTP.Headers['X-API-KEY'] = APIKEY

    HTTP.CacheTime = 0
def ValidatePrefs():
	if Prefs['usr'] and Prefs['pwd']:
		YouseeUsersLogin(Prefs['usr'], Prefs['pwd'])
		
def VideoMainMenu():
	dir = ObjectContainer(view_group = "List", title1 = NAME, title2 = NAME, art = R(ART))
	
#	Log.Debug(YouseeUsersLogin(Prefs['usr'], Prefs['pwd']))
	if Prefs['usr'] and Prefs['pwd']:
		YouseeUsersLogin(Prefs['usr'], Prefs['pwd'])
	usr = YouseeUsersUser()

	dir.add(DirectoryObject(title = "Live TV", key = Callback(YouseeLiveTVAllowed_channels)))
	#@TODO: waiting for yousee to fix archive
#	dir.add(DirectoryObject(title = 'TV Arkiv', key = Callback(YouseeArchiveMenu)))
	# VOD Subscription
	Log.Debug(YouseeUsersUser())
	if usr.get('hassvod'):
		pass
	dir.add(PopupDirectoryObject(key = Callback(YouseeSettings), title = 'YouSee indstillinger'))
	dir.add(PrefsObject(title = 'Plex Indstillinger'))
	return dir

def YouseeSettings():
	dir = ObjectContainer(view_group = 'List', title1 = NAME, title2 = 'YouSee indstillinger')
	dir.add(PopupDirectoryObject(key = Callback(YouseeUsersDevices), title = 'Enheder'))
	
	return dir

def YouseeArchiveMenu():
	dir = ObjectContainer(view_group = 'List', title1 = NAME, title2 = 'TV Arkiv')
	dir.add(DirectoryObject(title = 'By genre', key = Callback(YouseeArchiveGenres)))
	dir.add(DirectoryObject(title = 'By channel', key = Callback(YouseeArchiveAllowed_channels)))
	return dir
	
	
#def YouseeSettingsDevices():
#	dir = ObjectContainer(view_group = 'List', title1 = NAME, title2 = 'YouSee indstillinger')
#	#dir.add(PopupDirectoryObject(key = Callback(YouseeSettings), title = 'Enheder'))
##	Log.Debug(YouseeUsersDevices())
#	return dir
	

#===============================================================================
#   
# Yousee API
#   
#===============================================================================

# Returns metadata for channel based on channel id.
def YouseeLiveTVchannel(id):
	return JSON.ObjectFromURL(APIURL + 'livetv/channel/id/%s/json' % id)
# Returns channels sorted by most popular. 
# Based on data from yousee.tv
def YouseeLiveTVpopularChannels():
	return JSON.ObjectFromURL(APIURL + 'livetv/popularchannels/json')
# Returns channels available for streaming from requesting ip address
def YouseeLiveTVAllowed_channels(clientip = Network.PublicAddress, branch = 'yousee', apiversion = 2):
	dir = ObjectContainer(view_group = 'List', title1 = NAME, title2 = 'Live TV', art = R(ART) )
##		nowandnext = Tvguide().nowandnext()
##		Log.Debug(nowandnext)
	channels = JSON.ObjectFromURL( APIURL + 'livetv/allowed_channels/branch/%s/clientip/%s/apiversion/%s/json' % (branch, clientip, apiversion))
	for channel in channels:
##		pass
		dir.add(VideoClipObject(url = 'http://yousee.tv/livetv/%s' % channel.get('shortname'), title = channel.get('nicename'), thumb = channel['logos'].get('mega') if channel['logos'].get('mega') != "" else channel['logos'].get('super') if channel['logos'].get('super') != ""else channel['logos'].get('extralarge') if channel['logos'].get('extralarge') != "" else channel['logos'].get('large') if channel['logos'].get('large') != "" else channel['logos'].get('small') if channel['logos'] != "" else R(ICON)))
	return dir
#Returns list of channels that should be presented to the user. NOTE: this is not the list of allowed channels.
#A non-yousee broadband user will get a list of channels
#from “Grundpakken”.
def YouseeLiveTVSuggested_channels():
	return JSON.ObjectFromURL(APIURL + 'livetv/suggested_channels/json')
#Returns absolute streaming URL for channel. Channel rights are based on client ip address.
def YouseeLiveTVStreamurl(channel_id, terminal, drmclientid, session_id, client = 'http', application = 'Plex'):
	return JSON.ObjectFromURL(APIURL + 'livetv/streamurl/channel_id/%s/client/%s/application/%s/erminal/%s/drmclientid/%s/json' % (channel_id, client, application, terminal, drmclientid), headers = {'X-Yspro':session_id})

# Returns meta data for one movie
def YouseeMovieMovieinfo( id,apiversion=2):
	return JSON.ObjectFromURL(APIURL + 'movie/movieinfo/id/%s/apiversion/2/json' % id)
# Returns all available themes
def YouseeMovieThemes( include100movies = 0, only100movies = 0, onlysvod = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/themes/include100movies/%s/only100movies/%s/onlysvod/%s/json' % (include100movies, only100movies, onlysvod))
# Returns all available genres
def YouseeMovieGenres(self, include100movies = 0, only100movies = 0,onlysvod = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/genres/include100movies/%s/only100movies/%s/onlysvod/%s/json' % (include100movies, only100movies, onlysvod))
# Returns all available movies
def YouseeMovieAll( sort = 'title', sortdirection = 'asc', offset = 0, limit = -1, include100movies = 0, excludetvseries = 0, onlysvod = 0, only100movies = 0, onlytvseries = 0, year = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/all/sort/%s/sortdirection/%s/offset/%s/limit/%s/include100movies/%s/excludetvseries/%s/onlysvod/%s/only100movies/%s/onlytvseries/%s/year/%s/json' % (sort, sortdirection, limit, include100movies, excludetvseries, onlysvod, only100movies, onlytvseries, year))
# Returns movies, moviepackages and tv show seasons based on search query
def YouseeMovieSearch( query, offset = 0, limit = -1, include100movies = 0, excludetvseries = 0, onlysvod = 0, only100movies = 0, onlytvseries = 0, apiversion = 2, year = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/search/query/%s/offest/%s/include100movies/%s/excludetvseries/%s/onlysvod/%s/only100movies/%s/onlytvseries/%s/apiversion/%s/year/%s/json' % (query, offset, limit, include100movies, excludetvseries, onlysvod, only100movies, onlytvseries, apiversion, year))
# Returns typeahead search terms
def YouseeMovieTypeahead_search( query, include100movies = 0, excludetvseries = 0, onlysvod = 0, only100movies = 0, onlytvseries = 0, year = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/typeahead_search/query/%s/include100movies/%s/excludetvseries/%s/onlysvod/%s/only100movies/%s/onlytvseries/%s/year/%s/json' % (query , include100movies, excludetvseries, onlysvod, only100movies, onlytvseries, year)) 
# Returns all movies in genre
def YouseeMovieIn_genre( genre, sort = 'title', sortdirection = 'asc', offset = 0, limit = -1, include100movies = 0, excludetvseries = 0, onlysvod = 0, only100movies = 0, onlytvseries = 0, year = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/in_genre/genre/%s/sort/%s/sortdirection/%s/offset/%s/limit/%s/include100movies/%s/excludetvseries/%s/onlysvod/%s/only100movies/%s/onlytvseries/%s/year/%s/json' % (genre, sort, sortdirection, offset, limit, include100movies, excludetvseries,  onlysvod, only100movies, onlytvseries, year))
# Returns all movies in theme
def YouseeMovieIn_theme( theme, sort = 'title', sortdirection = 'asc', offset = 0, limit = -1, include100movies = 0, excludetvseries = 0, onlysvod = 0, only100movies = 0, onlytvseries = 0, year = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/in_theme/theme/%s/sort/%s/sortdirection/%s/offset/%s/limit/%s/include100movies/%s/excludetvseries/%s/onlysvod/%s/only100movies/%s/onlytvseries/%s/year/%s/json' % (theme, sort, sortdirection, offset, limit, include100movies, excludetvseries, onlysvod, only100movies, onlytvseries, year))
#Returns related movies for movie.
#Data is based on matching genres orders by popularity
def YouseeMovieRelated( id, only100movies = 0, onlysvod = 0, onlytvseries = 0):
	return JSON.ObjectFromURL(APIURL + 'movies/related/id/%s/only100movies/%s/onlysvod/%s/onlytvseries/%s/json' % (id, only100movies, onlysvod, onlytvseries))
#Returns accepted payment methods for movie renting
def YouseeMovieSupported_payment_methods( amount):
	return JSON.ObjectFromURL(APIURL + 'movies/supported_payment_methods/amount/%s/json' % amount)
#Creates order in yousee.tv backend. This is first step in the two-step procedure for generating orders
def YouseeMovieOrder( yspro, id, reference_id, client_ip = Network.PublicAddress, ytype = 'movie'):
	return JSON.ObjectFromURL(APIURL + 'movies/order/id/%s/reference_id/%s/client_ip/%s/type/%s/json' % (id, reference_id, client_ip, ytype), headers = {'X-Yspro':yspro})
#Confirms order in yousee.tv backend. This is the second step in the two-step procedure for generating orders.
#A receipt is sent to the customer upon successful confirmation of order
def YouseeMovieOrder_confirm( yspro, order_id, transaction_id, pincode, giftcode, trust, fee):
	url = 'movies/order_confirm/order_id/%s/' % (order_id, transaction_id)
	if pincode: 
		url += 'pincode/%s/' % pincode
		trust = True
	if giftcode:
		url += 'giftcode/%s/' % giftcode
		trust = True
	if trust:
		url += 'trust/true/'
	url += 'fee/%s/json' % fee
	return JSON.ObjectFromURL(APIURL + url, headers = {'X-Yspro':yspro})
# Returns information needed for embedding player.
def YouseeMoviePlayerdata( yspro, id):
	return JSON.ObjectFromURL(APIURL + 'movies/playerdata/id/%s/json' % id, headers = {'X-Yspro':yspro})
# Returns HLS streaming URL
def YouseeMovieStreamurl( session_id, id, drmclientid, application = 'Plex', terminal = 'Plex_9'):
	return JSON.ObjectFromURL(APIURL + 'movies/streamurl/id/%s/application/%s/terminal/%s/drmclientid/%s/json' % (id, application,terminal,drmclientid), headers = {'X-Yspro':session_id})
# Returns all or subset of moviepackages
def YouseeMovieMoviepackages( sort = 'name', sortorder = 'asc', offset = 0, limit = -1):
	return JSON.ObjectFromURL(APIURL + 'movie/moviepackages/sort/%s/sortorder/%s/offset/%s/limit/%s/json' % (sort, sortorder, offset, limit))
# Returns a single moviepackage
def YouseeMovieMoviepackage():
	return JSON.ObjectFromURL(APIURL + 'movie/moviepackage/id/%s/json' % id)
# Returns all or subset of tvshows
def YouseeMovieTvshows( offset = 0, limit = -1, only100movies = 0, onlysvod = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/tvshows/offset/%s/limit/%s/only100movies/%s/onlysvod/%s/json' % (offset, limit, only100movies, onlysvod))
# Returns a single tv show
def YouseeMovieTvshow( id, only100movies = 0, onlysvod = 0):
	return JSON.ObjectFromURL(APIURL + 'movie/tvshow/id/%s/only100movies/%s/onlysvod/%s/json' % (id, only100movies, onlysvod))
# Returns a single tv show season
def YouseeMovieTvshowseason( id, only100movies=0, onlysvod =0):
	return JSON.ObjectFromURL(APIURL + 'movie/tvshowseason/id/%s/only100movies/%s/onlysvod/%s/json' % (id,only100movies,onlysvod))

# Returns meta data for one album
def YouseePlayAlbum(id):
	return JSON.ObjectFromURL( APIURL + 'play/album/id/%s/json' % id)
# Returns meta data for one track
def YouseePlayTrack(id):
	return JSON.ObjectFromURL( APIURL + 'play/track/id/%s/json' % id)
# Returns meta data for one artist
def YouseePlayArtist(id):
	return JSON.ObjectFromURL( APIURL + 'play/artist/id/%s/json' % id)
# Returns discography
def YouseePlayArtist_discography( id, offset = 0, limit = 5):
	if limit >50: limit = 50
	return JSON.ObjectFromURL( APIURL + 'play/artist_discography/id/%s/json' % id)
# Returns playlist metadata and tracks
def YouseePlayPlaylist(self, hash):
	return JSON.ObjectFromURL( APIURL + 'play/playlist/id/%s/json' % id)
# Returns editorial list
def YouseePlayList(self, ylist):
	return JSON.ObjectFromURL(APIURL + 'play/list/json')
# Returns all available channels in TV guide, sorted by categories
def YouseeTvguideChannels( u= "", m = "", v = ""):
	url = APIURL + 'tvguide/channels/'
	if u != "":
		url += 'u/%s/' % u
	if m != "":
		url += 'm/%s/' %m
	if v != "":
		url += 'v/%s/' % v
	url += 'json'
	meta = JSON.ObjectFromURL(url)
	return meta
# Returns all categories
def YouseeTvguideCategories():
	return JSON.ObjectFromURL(APIURL + 'tvguide/categories/json')
# Returns programs
def YouseeTvguidePrograms( channel_id = "", offset = -1, tvdate = datetime.date.today()):
	url = APIURL + 'tvguide/programs/'
	if channel_id != "":
		url += 'channel_id/%s/' % channel_id
	if offset >= 0:
		url += 'offset/%s/' % offset
	if tvdate != datetime.date.today():
		url += 'tvdate/%s%' % tvdate.strftime('%Y-%m-%d')
	url += 'json'
	return JSON.ObjectFromURL(url)
# Returns single program
def YouseeTvguideProgram( id):
	return JSON.ObjectFromURL(APIURL + 'tvguide/program/id&%s/json' % id)
# Returns programs matching query
def YouseeTvguideSearch( query, offset = 0, limit = 10):
	return JSON.ObjectFromURL(APIURL + 'tvguide/search/query/%s/offset/%s/limit/%s/json' % (query, offset, limit))
# Returns a list of recommended programs
def YouseeTvguideRecommendedprograms( poplimit = 10, morelimit = 10):
	return JSON.ObjectFromURL(APIURL + 'tvguide/recommendedprograms/poplimit/%s/morelimit/%s/json' % (poplimit, morelimit))
# returns programlist with now and next information for all streamable channels
def YouseeTvguideNowandnext():
	return JSON.ObjectFromURL(APIURL + 'tvguide/nowandnext/json')
#Returns a list of genres
def YouseeArchiveGenres():
	dir = ObjectContainer(view_group = 'List', title1 = NAME, title2 = 'Archive Genres')
	genres =  JSON.ObjectFromURL(APIURL + 'archive/genres/json')
	for genre in genres:
		dir.add(DirectoryObject(title = genre.get('name'), key = Callback(YouseeArchivePrograms, genre_id = genre.get('id'))))
	return dir
# Returns a list of programs in archive
def YouseeArchivePrograms(channel_id = None, genre_id = None, tvdate = None ):
	dir = ObjectContainer(view_group = 'List', title1 = NAME)
	url = APIURL + 'archive/programs/'
	if channel_id:
		url += 'channel_id/%s/' % channel_id
	if genre_id:
		url += 'genre_id/%s/' % genre_id
	if tvdate:
		url += 'tvdate/%s/' % Datetime.ParseDate(tvdate).strftime('%Y-%m-%d')
	url += 'json'
	programs = JSON.ObjectFromURL(url)
	for program in programs:
		#@TODO get the right URL
		dir.add(VideoClipObject(title = program.get('title'), url = 'http://yousee.tv/arkiv/%s' % 'test'))
	return dir
# Returns a list of allowed archive channels
def YouseeArchiveAllowed_channels():
	dir = ObjectContainer(view_group = 'List', title1 = NAME)
	channels = JSON.ObjectFromURL(APIURL + 'archive/allowed_channels/json')
	for channel in channels:
		dir.add(DirectoryObject(title = channel.get('nicename'), key = Callback(YouseeArchivePrograms, channel_id = channel.get('id'))))
		Log.Debug(channel)
	return dir
# Returns a list of programs in archive matching search query
def YouseeArchiveSearch( query):
	return JSON.ObjectFromURL(APIURL + 'archive/search/query/%s/json' % query)
# Returns absolute streaming url for content
def YouseeArchiveStreamurl( id):
	return JSON.ObjectFromURL(APIURL + 'archive/streamurl/id/%s/json' % id)

# Logs in user and returns YS Pro session information
def YouseeUsersLogin( username, password):
	login = JSON.ObjectFromURL(APIURL+  'users/login/username/%s/password/%s/json' % (username, password))
	if 'session_id' in login:
		Data.Save('session_id', login.get('session_id'))
		return True
	else:
		return False
	
#	return JSON.ObjectFromURL(APIURL+  'users/login/username/%s/password/%s/json' % (username, password))
# Logs out user of YSPro
def YouseeUsersLogout():
	return JSON.ObjectFromURL(APIURL + 'users/logout/json')
# Creates new user in YSPro backend
def YouseeUsersUser():
	return JSON.ObjectFromURL(APIURL + 'users/user/json')
# Returns transaction log for user
def YouseeUsersTransactions():
	return HTTP.Request(APIURL + 'users/transactions/json')
		
# Checks if user is using YouSee Broadband
def YouseeUsersIsyouseeip():
	return JSON.ObjectFromURL(APIURL + 'users/isyouseeip/json')

# Checks if user has access to movie
def YouseeUsersMovieaccess():
	return JSON.ObjectFromURL(APIURL + 'users/movieaccess/json')
# Refreshes usersession in YSPro backend
def YouseeUsersKeepalive():
	return JSON.ObjectFromURL(APIURL + 'users/keepalive/json')
# Returns device list
def YouseeUsersDevices(customerno = "", udid = ""):
	dir = ObjectContainer(view_group = "List", title1 = NAME, title2 = 'Enheder', art = R(ART))
	url = APIURL + 'users/devices/'
	if customerno != "":
		url += 'customerno/%s/' % customerno
	if udid != "":
		url += 'udid/%s/' % udid
	url += 'format/json'
	
	if udid != "":
		devices = JSON.ObjectFromURL(url)
		
		expDate = Datetime.ParseDate( devices.get('devices')[0].get('expires'))-Datetime.Now()
		dir.add(PopupDirectoryObject(title = 'Info', key = Callback(infobox, title = devices.get('devices')[0].get('name'), message = "Expires in %s days" % expDate.days )))
		dir.add(PopupDirectoryObject(title = 'Delete', key = Callback(YouseeUsersDevice, udid = udid, method = "DELETE")))
	else:
		devices = JSON.ObjectFromURL(url)
		for device in devices.get('devices'):
			dir.add(PopupDirectoryObject(title = device.get('name'), key = Callback(YouseeUsersDevices, udid = device.get('udid'))))
		if len(devices.get('devices')) < int(devices.get('device_limit')):
			dir.add(InputDirectoryObject(title = 'Add Device', key = Callback(YouseeUsersDevice, method = "POST"), prompt = 'Navn'))
	return dir
# POST: Add new device to device list
# DELETE: Remove device from list
def YouseeUsersDevice(udid = "", name = "", method = "POST", query = ""):
	dir = ObjectContainer(view_group = "List", title1 = NAME, title2 = 'Enhed', art = R(ART))
	# Add Device
	if method == "POST":
		try:
			
			deviceMsg = HTTP.Request(APIURL + 'users/device/format/json', values = {'udid':Platform.MachineIdentifier, 'name':query})

#			dir.add(PopupDirectoryObject(title = 'Device Info', key = Callback(YouseeUsersDevice(udid = udid))))
			dir.header = 'Device Added'
			dir.message = 'Plex Media Server can now be used on a non YouSee connection'
		except:
			dir.header = 'Error'
			dir.message = JSON.ObjectFromString(deviceMsg.content).get('status', 'Unknown Error')

#	 Delete Device
	elif method == 'DELETE':
		if udid !="":
			try:
				deviceMsg = HTTP.Request(APIURL + 'users/device/udid/%s/format/json' % udid, method = 'DELETE')
				dir.header = "Device deleted"
				if JSON.ObjectFromString( deviceMsg.content).get('status') != 'ok':
					raise RuntimeError(JSON.ObjectFromString( deviceMsg.content).get('status'))
			except Exception, err:
				dir.header = 'Error'
				dir.message = str(err)
	return dir
		
	
def YouseeUsersGenerate_deviceid():
	return JSON.ObjectFromURL(APIURL + 'users/generate_deviceid/format/json')
# Returns favorites
def YouseeUsersFavorites():
	return JSON.ObjectFromURL(APIURL + 'users/favorites/json')
# POST: Add new favorite
# DELETE: Remove a favorite
def YouseeUsersFavorite( method = 'POST'):
	return JSON.ObjectFromURL(APIURL + 'users/favorite/json')
# Sorts favorites in list
def YouseeUsersFavorites_sortorder():
	pass
# POST: Saves bookmark in seconds
# GET: Returns bookmark
# DELETE: Removes bookmark
def YouseeUsersBookmark(method = 'GET'):
	pass
# Returns all bookmarks
def YouseeUsersBookmarks():
	return JSON.ObjectFromURL(APIURL + 'users/bookmarks/json')
# POST: Add new movie log entry
# GET: Returns movie log
# DELETE: Resets movielog
def YouseeUsersMovielog( method = 'GET'):
	pass
# Returns data for filmshelf
def YouseeUsersFilmshelf():
	return JSON.ObjectFromURL(APIURL + 'users/filmshelf/json')

# Returns current supportmessage
def YouseeSystemSupportmessage():
	return JSON.ObjectFromURL(APIURL + 'system/supportmessage/json')
# Returns latest errormessage for device
def YouseeSystemErrormessage( udid):
	return JSON.ObjectFromURL(APIURL + 'system/errormessage/udid/%s/json' % udid)

# build the rest URL
def kwargsToURL(url, **kwargs):
	
	for ysArgs in kwargs:
		url += ysArgs + '/' + kwargs[ysArgs]
	url += 'json'
	return url
def infobox(title, message):
	return ObjectContainer(view_group = 'List', header = title, message = message)
			