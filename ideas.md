## To do, P0
- Add `musttick`. Whenever there is a musttick, make autoschedule _force_ a transition. Do this by just cutting the current video and jumping a second forward.
- Zoom out currently loses a frame. Fix this. Also, allow different zoom speeds.
- Just recode zoom entirely. I think resize messes with resolution stuff.
- Audio or video cues for auto light. Eg speech to text, cue with “this is cool” or something like that
- Just diretly use FFMPEG, see ffmpeg section below

## To do, P1
- Look into [`av` python library](https://pyav.basswood-io.com/docs/stable/index.html).
- Convolve in both directions, and with different size filters
- Make autoaudioticks better. Maybe use [Essentia](https://essentia.upf.edu/tutorial_rhythm_beatdetection.html). or maybe [this](https://mziccard.me/2015/05/28/beats-detection-algorithms-1/#:~:text=The%20algorithm%20divides%20the%20data,considered%20to%20contain%20a%20beat.), although I basically already do this.
- Fade text, `bg_color` needs to be transparent: [https://github.com/Zulko/moviepy/issues/400](https://github.com/Zulko/moviepy/issues/400). Possibly use masks?
- I think width/height doesn't work. Only resolution works. That might be because I still need to keep `concatenate_videos` with `method='compose`. Not sure.
- Instead of needing to supply `portrait=True`, somehow check to see if moviepy automatically rotated the image/video for some reason.
- Add option to allow portrait images to have their black sides.
- Allow a video option to be audio fade in. More generally, allow an option so that during a certain video or a certain part of a video, the music fades out a little while the audio from the video fade in a little, and then fades out while the music fades back in. The way to do this is probably to allow a Clip to have `fadeout_audio`, `fadein_audio`, and `bg_audio_volume`. The `fadeout_audio` option fades out the audio from the video, and similarly for fadein. The `bg_audio_volume` fades out the the background audio to that volume, then keeps it there for the duration of the video clip, then fades the background audio back in to its original volume. We just need to get the timing of the video clip, then split the audio at that time and work with the audio.
- New/alternative algorithm for autoschedule, see divide and conquer section below



## FFMPEG
- Nice [intro](https://alexandrehtrb.github.io/posts/2025/01/introduction-to-ffmpeg/) to ffmpeg
- [Speed up video without changing audio pitch](https://ffmpegbyexample.com/examples/749f6u35/timestretch_audio_and_video_using_rubberband_filter/)
- [Create video from image](https://stackoverflow.com/questions/24961127/how-to-create-a-video-from-images-with-ffmpeg). `ffmpeg -framerate 1/3 -start_number 0 -i test_%d.png -vcodec mpeg4 test.mp4` for three seconds for each image. Can do zoom and zoompan, etc.
- Get video duration: `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 filename.filetype`



## Divide and conquer algorithm

Divide and conquer might be optimal. 

- Suppose we have N clips of duration T d1, …. T dN. 
- We will turn the ith clip into length li T, with li= ri di. 
- We have a set of ticks at times T mk, with M ={mk}. 
- The transitions are at ti T, with ti = \sum_{j=1}^i li. 
- Our objective is to minimize Var(r) such that ti \in M and tN = 1. 
- Let this optimal solution be r = Solve(d, m). 
- For closure, let Solve(d, m, u) be the minimum of Var(r) such that ti \in M and tN = u. 

- suppose I have the optimal r = Solve(d, m, 1). From this r, compute t. 
- Chose some arbitrary i (eg i=N/2)
- Let k be the k such that ti = mk. 
- My claim is that the (r1, …, ri) = Solve((d1,…,di), m, ti) and similarly (ri+1,…,rN) = Solve((di+1,…,dN), m-ti, 1-ti). This is not true (see below) unless d1=d2=.... But I think it is potentially a good heuristic algorithm.

<!-- - The reason is something like this maybe. 
- Once we have the optimal k, the left half is fixed to have total duration ti = mk. This means that the first i clips need to exactly fit in time mk. 
- This means that the left and right halves become two separate problems. We can easily change the variance of the left half without changing the variance of the right half. So suppose we keep the right half fixed but lower the the variance of the left half. Then the global variance would also be lower. This contacts the global minimality assumption. 
- Specifically, Var(r) = 1/N suma ra^2 - 1/N^2 sum_{ab} ra rb = () Var(left) + () Var(right) - sum_{left} rleft sum_right right.  Hm, it’s the second term I don’t know what to do with.
- In the special case that all the di’s are the same, r lies in the simplex. So we get () Var(left) + () Var(right) - sum_{left} rleft (1-sum left). So we see that the right hand side is completely desperate. Ie we know r = min left min right. 
- Need to write out the full Var(r) calculation carefully. 

If I can make it work, then this means that we can divide and conquer to efficiently solve this. 
s



- Constraint ti \in M, tN = 1
- ri = (ti - t{i-1}) / di
- Minikize 1/N sum_i (ti - t{i-1})^2 / di^2 - 1/N^2 (sum_i (ti - t{i-1}) / di)^2
- Suppose the optimal for  i=a is ta = mk.
- Fixing this ta, we have the whole thing is equal to Minikize Var(left) + Var(right) - (sum_left (ti - t{i-1}) / di) (sum_right (ti - t{i-1}) / di)
 -->


When the dis are equal, I think we can show the divide and conquer algorithm arrives  at unique solution. Basically when N is small (eg 2), we can show that there are only a small possible degeneracy (2?). So the full algorithm runtime is something like 2^log N. 
