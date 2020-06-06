import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=str, default='images')
    args = parser.parse_args()
    # Generate annotation visualizations
    os.system('python vis.py --dir {}'.format(args.dir))
    # Make a video of rendered RGB frames
    os.system('cd ./{} && ffmpeg -y -framerate 15 -i %06d_rgb.png -pix_fmt yuv420p out.mp4 && cd ..'.format(args.dir))
    # Make a video of rendered annotations
    os.system('cd ./annotated && ffmpeg -y -framerate 15 -i %06d_annotated.png -pix_fmt yuv420p out.mp4 && cd ..')
    # Concatenate videos side by side
    os.system("ffmpeg -y -i {}/out.mp4 -i annotated/out.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast output.mp4".format(args.dir))
