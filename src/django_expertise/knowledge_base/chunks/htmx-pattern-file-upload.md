# File Upload with Progress Bar

- **ID:** `htmx-pattern-file-upload`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: File Upload with Progress
- **Tags:** `htmx`, `upload`, `multipart`, `progress`

## Canonical pattern (Django / HTMX / Hyperscript way)
Set hx-encoding='multipart/form-data' on the form so files upload, and listen to htmx:xhr:progress via hx-on to drive a progress bar from event.detail.loaded/total. The view handles request.FILES normally.

## Laravel / MVC default (what AI typically generates)
AI uses axios with onUploadProgress and FormData, or a dropzone library, posting to a JSON endpoint and rendering the result client-side. FormData + fetch boilerplate everywhere.

## Why Django differs
hx-encoding is the one attribute that flips HTMX into multipart mode; Django's request.FILES handling is unchanged. Progress is exposed as an HTMX event, fitting the hx-on Phase-1 pattern with a couple of lines of vanilla JS.

## Example
<form hx-post="{% url 'document-upload' %}" hx-target="#upload-result"
      hx-encoding="multipart/form-data"
      hx-on:htmx:xhr:progress="
        const progress = event.detail.loaded / event.detail.total * 100;
        document.getElementById('progress-bar').style.width = progress + '%';">
  <input type="file" name="document" accept=".pdf,.docx">
  <button type="submit">Upload</button>
  <div class="progress"><div id="progress-bar" class="progress-bar" style="width:0%"></div></div>
</form>

# views.py
doc = Document(file=request.FILES['document']); doc.save()
return render(request, 'documents/_uploaded.html', {'doc': doc})
