import os, subprocess, sys, glob, tempfile
from PIL import Image
import imageio_ffmpeg

src, out = sys.argv[1], sys.argv[2]
sec = float(sys.argv[3]) if len(sys.argv) > 3 else 2.4
ff = imageio_ffmpeg.get_ffmpeg_exe()
slides = sorted(glob.glob(os.path.join(src, 'slide*.jpg')))
assert slides, 'no slides'
tmp = tempfile.mkdtemp()
frames = []
for i, p in enumerate(slides):
    im = Image.open(p).convert('RGB')
    canvas = Image.new('RGB', (1080, 1920), '#F6F6F6')
    canvas.paste(im, (0, (1920 - 1350) // 2))
    f = os.path.join(tmp, f'f{i:02d}.png')
    canvas.save(f)
    frames.append(f)
cmd = [ff, '-y']
for f in frames:
    cmd += ['-loop', '1', '-t', str(sec + 0.5), '-i', f]
n = len(frames)
fade = 0.5
flt, last = [], '[0:v]'
for i in range(1, n):
    flt.append(f'{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={round(i*sec,2)}[v{i}]')
    last = f'[v{i}]'
cmd += ['-filter_complex', ';'.join(flt), '-map', last, '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '20', '-movflags', '+faststart', '-an', out]
subprocess.run(cmd, check=True, capture_output=True)
print(out)
