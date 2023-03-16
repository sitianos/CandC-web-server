from .models import Account, Puppet, directory_path

from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    FileResponse
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.signing import TimestampSigner

import urllib.request
import urllib.parse
from pathlib import Path

@login_required(login_url="admin:login")
def index(request):
    return HttpResponse("\n".join(["<p>{}:{}</p>".format(i[0],i[1]) for i in request.headers.items()]))

def send_notify(message=""):
    url = "https://notify-api.line.me/api/notify"
    payload = urllib.parse.urlencode({'message' : message}).encode('ascii')
    try:
        req = urllib.request.Request(url,data=payload)
        req.add_header("Authorization","Bearer " + settings.LINE_TOKEN)
        res = urllib.request.urlopen(req)
        return res
    except:
        return

@csrf_exempt
def notify(request):
    try:
        if request.method == 'GET':
            mes = request.GET.get('notify','')
            uid = request.GET.get('uid')
        else:
            mes = request.POST.get('notify','')
            uid = request.POST.get('uid')
        if not uid:
            return HttpResponseBadRequest("No uid")
        try:
            pup = Puppet.objects.get(uid=uid)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Bad uid")
        addr = request.META['REMOTE_ADDR'] or request.headers.get('X-Forwarded-For')
        message = f'message from {pup.username} {addr}\n{mes}'
        res = send_notify(message)
        if res:
            return HttpResponse(f'notified {res.status}')
        else:
            return HttpResponseBadRequest("Failed to send notification")
    except Exception as e:
        send_notify("server error", " ".join(e.args))
        return HttpResponseBadRequest("Server Error")

@csrf_exempt
def action(request):
    try:
        if request.method == 'GET':
            uid = request.GET.get('uid')
        else:
            uid = request.POST.get('uid')
        if not uid:
            return HttpResponseBadRequest("No uid")
        try:
            pup = Puppet.objects.get(uid=uid)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Bad uid")
        now = timezone.localtime()
        delta = now - pup.last_access
        if delta.seconds > 660:
            addr = request.META['REMOTE_ADDR'] or request.headers.get('X-Forwarded-For')
            send_notify(f"acccess from {pup.username} {addr}")
        pup.last_access = now
        pup.save()
        signer = TimestampSigner()
        token = signer.sign(uid)
        functions = {
            "once": f"""function once {{
PRE=/tmp/once_lock_
LOCK=${{PRE}}$(echo -n "$@" | md5sum | cut -f1 -d" ")
if [ ! -f $LOCK ]
then
  rm -f $PRE*
  touch $LOCK
  eval $@
fi
}}
""",
            "upload": f"""function upload {{
TOKEN="{token}"
for UP in $*
do
  [ -f $UP ] && curl "{request.build_absolute_uri(reverse("upload"))}" -f -X POST -F "upload=@$UP" -F "token=$TOKEN"
done
}}
""",
            "notify": f"""function notify {{
wget "{request.build_absolute_uri(reverse("notify"))}" --post-data "uid={uid}&notify=$(eval $@ 2>&1)" -O /dev/null -o /dev/null
}}
""",
            "result": f"""function result {{
RESULT=/tmp/result_$1.txt
eval $@ > $RESULT 2>&1
TOKEN="{token}"
curl "{request.build_absolute_uri(reverse("upload"))}" -f -X POST -F "upload=@$RESULT" -F "token=$TOKEN"
rm $RESULT
}}
"""
        }

        commands = ""
        for cmd, func in functions.items():
            if cmd in pup.cmd:
                commands += func

        commands += pup.cmd.replace('\r', '')
        return HttpResponse(commands)
    except Exception as e:
        send_notify("server error", " ".join(e.args))
        return HttpResponseBadRequest("Server Error")

@csrf_exempt
def upload(request):
    if request.method == 'POST':
        try:
            file = request.FILES.get('upload')
            token = request.POST.get('token')
            if token:
                try:
                    signer = TimestampSigner()
                    uid = signer.unsign(token, max_age=60)
                    pup = Puppet.objects.get(uid=uid)
                except:
                    return HttpResponseBadRequest("Bad Token")
            else:
                return HttpResponseBadRequest("No Token")
            if not file:
                return HttpResponseBadRequest("No File")

            exists = default_storage.exists(directory_path(pup, file.name))

            total_size=0
            dir=directory_path(pup, '')
            if default_storage.exists(dir):
                total_size = sum((default_storage.size(dir + f) for f in default_storage.listdir(dir)[1]
                    if f != file.name))

            if total_size + file.size > 1024**3:
                send_notify(f'{pup.username} failed to upload {file.name}:{file.size}iB because of capacity over from {addr}')
                return HttpResponseBadRequest("Capacity Over")

            if exists:
                default_storage.delete(dir + file.name)

            pup.upload_file = file
            pup.save()
            addr = request.META['REMOTE_ADDR']
            if exists:
                send_notify(f'{pup.username} replaces {file.name}({file.size}iB) from {addr}')
            else:
                send_notify(f'{pup.username} uploads {file.name}({file.size}iB) from {addr}')

            return HttpResponse(f'upload {file.name}')
        except Exception as e:
            send_notify(" ".join(e.args))
            return HttpResponseBadRequest("Failed to upload file")
    else:
        return HttpResponseBadRequest("Bad Method")

@login_required(login_url="admin:login")
def download(request, path="./"):
    ospath=Path(default_storage.path(path))
    if ospath.is_dir():
        if not path.endswith('/'):
            return redirect("download", path=path+'/')
        message=""
        if request.method == "POST" and "delete" in request.POST:
            delete=request.POST.getlist("delete")
            for dfile in delete:
                if default_storage.exists(path+dfile):
                    default_storage.delete(path+dfile)
                    message+=f"{dfile} deleted. "
                else:
                    message+=f"{dfile} does not exist. "
        context = dict()
        context['dir_list'] = sorted(default_storage.listdir(path)[0])
        file_list  = [{'name':file, 'time':default_storage.get_created_time(path+file), 'size':default_storage.size(path+file)} for file in default_storage.listdir(path)[1]]
        context['file_list'] = sorted(file_list, key=lambda f:(f['time'],f['name'],f['size']))
        context['path'] = path
        context['message'] = message
        context['total_size'] = sum([f['size'] for f in file_list])
        return render(request, 'candc/download.html', context)
    elif ospath.is_file():
        f = default_storage.open(path,"rb")
        return FileResponse(f, filename=ospath.name)
    else:
        return HttpResponse("<p>not exist "+path+"</p>\n"+"<a href=\"..\">../</a>")
