from PIL import Image, ImageOps, ImageFilter, ImageEnhance
S='/mnt/user-data/uploads/Desktop/GINTER/sajt/materijali/foto/'
A='/mnt/user-data/attachments/bd42655e-adf2-553c-8ee4-c8b90d65e91f/b0ca3676-image.png'
OUT='/home/claude/site/img/'
def load(p): return ImageOps.exif_transpose(Image.open(p)).convert('RGB')
def soft(im, w, blur, contrast=0.94, sat=0.95):
    r=im.copy(); r=r.resize((w, round(im.height*w/im.width)), Image.BICUBIC)
    r=r.filter(ImageFilter.GaussianBlur(blur))
    r=ImageEnhance.Contrast(r).enhance(contrast); r=ImageEnhance.Color(r).enhance(sat)
    return r
def save(im,name,w,blur,**k): soft(im,w,blur*w/1000,**k).save(f'{OUT}{name}-{w}.webp','WEBP',quality=78,method=6)
for n,src in []:
    im=load(src)
    for w in (600,1000): save(im,n,w,1.4,contrast=0.9,sat=0.92)
h=load(S+'salon2.jpg')
for w in (960,1600,2400): save(h,'hero',w,1.0,contrast=0.9)
s=load(S+'salon.jpg')
for w in (800,1400): save(s,'salon',w,1.0,contrast=0.9)
f=s.crop((s.width//2,0,s.width,s.height))
for w in (800,1600): save(f,'frames',w,1.0,contrast=0.9)
print('ok')

# Ervin & Bojana: soft-focus — смесь чёткого и размытого (детали остаются, кожа мягче)
def glow(im, w, mix=0.35, rad=2.4):
    r=im.resize((w, round(im.height*w/im.width)), Image.LANCZOS)
    b=r.filter(ImageFilter.GaussianBlur(rad*w/1000))
    r=Image.blend(r,b,mix)
    return ImageEnhance.Color(ImageEnhance.Contrast(r).enhance(0.94)).enhance(0.95)
for n,src in (('anna',A),):
    im=load(src)
    for w in (600,1000): glow(im,w).save(f'{OUT}{n}-{w}.webp','WEBP',quality=82,method=6)
print('glow ok')

# Ervin & Bojana: уже смягчены Анной — только уменьшаем, без обработки
ATT='/mnt/user-data/attachments/bd42655e-adf2-553c-8ee4-c8b90d65e91f/'
for n,f in (('bojana','5f2d3877-image.png'),('ervin','596889c9-image.png')):
    im=load(ATT+f)
    for w in (600,1000):
        im.resize((w, round(im.height*w/im.width)), Image.LANCZOS).save(f'{OUT}{n}-{w}.webp','WEBP',quality=85,method=6)
print('owners ok')
