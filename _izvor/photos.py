from PIL import Image, ImageOps, ImageFilter, ImageEnhance
S='/mnt/user-data/uploads/Desktop/GINTER/sajt/materijali/foto/'
A='/mnt/user-data/attachments/bd42655e-adf2-553c-8ee4-c8b90d65e91f/c920650a-image.png'
OUT='/home/claude/site/img/'
def load(p): return ImageOps.exif_transpose(Image.open(p)).convert('RGB')
def soft(im, w, blur, contrast=0.94, sat=0.95):
    r=im.copy(); r=r.resize((w, round(im.height*w/im.width)), Image.BICUBIC)
    r=r.filter(ImageFilter.GaussianBlur(blur))
    r=ImageEnhance.Contrast(r).enhance(contrast); r=ImageEnhance.Color(r).enhance(sat)
    return r
def save(im,name,w,blur,**k): soft(im,w,blur*w/1000,**k).save(f'{OUT}{name}-{w}.webp','WEBP',quality=78,method=6)
for n,src in [('ervin',S+'ervin.jpg'),('bojana',S+'bojana.jpg'),('anna',A)]:
    im=load(src)
    for w in (600,1000): save(im,n,w,0.9)
h=load(S+'salon2.jpg')
for w in (960,1600,2400): save(h,'hero',w,0.6)
s=load(S+'salon.jpg')
for w in (800,1400): save(s,'salon',w,0.6)
f=s.crop((s.width//2,0,s.width,s.height))
for w in (800,1600): save(f,'frames',w,0.6)
print('ok')
