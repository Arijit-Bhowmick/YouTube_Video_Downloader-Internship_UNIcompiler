from logging import error
import ffmpeg
from pytube import YouTube
import os
from datetime import datetime
import json
import curses
import sys

class DownloadYTVideo:
    '''
    Download Youtube Video
    '''

    def __init__(self, arg=''):
        '''
        Defines Predefined Data to be assigned
        on each run
        '''
        
        self.download_location = 'Downloads'
        self.json_file_location = 'DOWNLOAD_JSON_DATA'
        self.video = 'Video'
        self.audio = 'Audio'
        self.resolution = '144p'
        self.arg = arg
        self.init_check = self.argCheck()
        self.download_file_data = {}

        if ('-h' in self.init_check) or ('-u' not in self.init_check):
            print(self.helpMsg())
            exit()

        if ('-d' in self.init_check) and (self.init_check['-d']!=''):
            self.download_location = self.init_check['-d']
        
        
        self.directoryCheck(self.json_file_location)
        self.directoryCheck(self.video)
        self.directoryCheck(self.audio)
        self.directoryCheck(self.download_location)
        self.screen = curses.initscr()
        
    def directoryCheck(self, directory):
        '''
        Directory Checks
        '''
        if os.path.isdir(directory)==False:
                os.mkdir(directory)
    def argCheck(self):
        '''
        Checks For Argument Incorrection

        returns Dictionary with
        Argument as Dictionary key and Argument Value as Dictionary Value
        '''
        value_required = ['-u']
        optional_arg = ['-d', '-res']
        value_not_required = ['-h']
        
        sorted_arg_data = {}

        for argument in self.arg[1::]:
            if argument.startswith('-'):
                if (argument in value_required+optional_arg+value_not_required):
                    try:
                        if (argument=='-u') or (argument=='-res'):
                            sorted_arg_data.update({argument:self.arg[self.arg.index(argument)+1].strip().split(' ')})

                        elif self.arg[self.arg.index(argument)+1] !='':
                            sorted_arg_data.update({argument:self.arg[self.arg.index(argument)+1]})
                    except:
                        sorted_arg_data.update({argument:''})

        return sorted_arg_data

    def helpMsg(self):
        '''
        Show this Message and Exit
        '''
        return f'''[[[YouTube Video Downloader]]]
Created By Arijit Bhowmick [sys41x4]

Usage python {self.arg[0]} -u <url> -res <resolution>

-u : URL of the YouTube Video to download
     Can be used with multiple URL's seperated
     with spaces and enclosed the urls as
     "<url_1> <url_2> <...>"

-res : Resolution of the YouTube Videos to Download
       Example : 144p, 720p, etc
       Can be used with multiple RESOLUTIONS's seperated
       with spaces and enclosing the values as
       "<res_1> <res_2> <...>"

       Default Resolution is : {self.resolution}

-d : Download Directory Path to download the YouTube Videos in.
     Default : {os.path.join(os.getcwd(), self.download_location)}
'''
    def combineVideoAudio(self, y, file_name):
        '''
        Combine Audio with Video
        '''

        try:
            self.printOutput(y, 0, f'{y-3} [Processing ]')
            video = ffmpeg.input(os.path.join(self.video, file_name))
            audio = ffmpeg.input(os.path.join(self.audio, file_name)).filter('volume', 5)
            ffmpeg.output(audio, video, os.path.join(self.download_location, file_name), strict='experimental', loglevel="quiet").run(overwrite_output=True)

            # Clean fragmented Video and Audio
            self.printOutput(y, 0, f'{y-3} [Cleaning Up]')
            os.remove(os.path.join(self.video, file_name))
            os.remove(os.path.join(self.audio, file_name))

        except error as e:
            self.printOutput(2, 10, e)
            curses.napms(7000)
            

    def downloadVideo(self, y, url, resolution='144p', video_type='mp4'):
        '''
        Download YouTube Video
        '''

        file_name = '[Fetching File Name]'
        status = ''
        audio_stream = 0
        try: 
            # object creation using YouTube
            # which was imported in the beginning 
            yt = YouTube(url)
            status = 'Connection Established'
            self.printOutput(2, 10, status)
            file_name = yt.title
            download_location = self.download_location

            

            video_stream = yt.streams.filter(res=resolution, mime_type=f"video/{video_type}", progressive="True")

            if len(video_stream)==0:
                video_stream = yt.streams.filter(res=resolution, mime_type=f"video/{video_type}")
                audio_stream = yt.streams.filter(mime_type=f"audio/{video_type}")


            # File Name Fixing
            for i in '''#<$+%>!`&*'|{?"=}/:\\@''':
                if (i in file_name)==True:
                   file_name = file_name.replace(i, " ")

            # Downloading Stream Datas
            if len(video_stream)!=0:
                video_stream=video_stream.first()
                
                if audio_stream!=0:
                    audio_stream=audio_stream.first()
                    download_location=self.video

                if (file_name+'.'+video_type in os.listdir(self.video)) or (file_name+'.'+video_type in os.listdir(self.audio)) or (file_name+'.'+video_type in os.listdir(self.download_location)):
                    file_name+=datetime.now().strftime(f"_{resolution}_[%d-%m-%Y_%H-%M-%S]")


                self.printOutput(y, 0, f'{y-3} [Downloading]')
                self.printOutput(y, 23, f'{file_name} :: {resolution} :: {url}')
                
                # Download Streams
                video_stream.download(download_location, file_name+'.'+video_type)
                if audio_stream!=0:
                    audio_stream.download(self.audio, file_name+'.'+video_type)

                    # Combine Video and Audio Streams
                    self.combineVideoAudio(y, file_name+'.'+video_type)
                self.printOutput(y, 0, f'{y-3} [Download Completed]')

            elif len(video_stream)==0:
                status = 'Connection Error'
                self.printOutput(y, 0, f'{y-3} [Download Error]')
                self.printOutput(y, 23, f'{file_name} :: {resolution} :: {url}')

        
        except:
            status = 'Connection Error'
            self.printOutput(2, 10, status)
            
            if file_name!='':
                status = '[Connection Error]'
                self.printOutput(y, 0, status)

        # Create JSON Data For Dumping
        self.download_file_data.update({
                y-4:{
                "url":url,
                "file_name":file_name+'.'+video_type,
                "resolution":resolution,
                "download_date": datetime.now().strftime(f"%d-%m-%Y %H:%M:%S"),
                "status":status
                }
            })
    

    def printOutput(self, y, x, text=''):
        '''
        Use to print synced Text [axis Based]
        as
        .___ x ___
        |
        y
        |
        '''
        self.screen.addstr(y, x, text)
        self.screen.refresh()

        

    def queueDownload(self):
        '''
        Download Videos in Que Format
        '''

        
        self.printOutput(0, 0, 'Created By Arijit Bhowmick [sys41x4]') # Banner Text
        self.printOutput(2, 0, 'STATUS : ')

        links = self.init_check['-u']
        try:
            resolutions = self.init_check['-res']
        except KeyError:
            resolutions=['']
        
        

        for i in range(len(links)):
            
            try:
                if resolutions[i]=='':
                    resolution = self.resolution
                else:
                    resolution = resolutions[i]
            except IndexError:
                resolution = self.resolution
            self.downloadVideo(i+4, links[i], resolution)


        json_object = json.dumps(self.download_file_data, indent=4)
        with open(datetime.now().strftime(f"{self.json_file_location}/%d-%m-%Y_%H-%M-%S.json"), "w") as outfile:
            outfile.write(json_object)
        
        self.printOutput(2, 10, "All Tasks Completed | Exiting in 5 seconds")
        curses.napms(5000)
        curses.endwin()
                    
                

yt_download = DownloadYTVideo(sys.argv)
yt_download.queueDownload()
        