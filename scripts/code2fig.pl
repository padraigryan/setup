#!/usr/bin/perl

use 5.010; # needed for the given statement

&get_switches_and_file_name;
&find_basename;
&read_in_code;
&read_in_transcript;
&create_xfig_header;
# &open_lyx_file;
# &print_lyx_header;
&parse_code;
&place_box;
&add_transcript;
&place_box;
&close_xfig_file;
&write_report;
# &print_lyx_footer;

#------------------------------------------------------------------------------
sub open_lyx_file {
   open LYX_OUT, ">$lyx_file" or die "[code2lyx.pl]: Can't open $lyx_file for writing\n";
   print "[code2fig.pl]: creating LyX file: lyx $lyx_file\n";
}


#------------------------------------------------------------------------------
sub write_report {
   print "[code2fig.pl]: Number of code lines is: $line_number \n";
   print "[code2fig.pl]: Number of comment-only lines is: $comment_only_line\n";
}

#------------------------------------------------------------------------------
sub get_switches_and_file_name {
   print "[code2fig.pl]: decoding command switches\n";

   $numArgs = $#ARGV + 1;
   $numbers = 0; # switching this on by default
   $comment_only_line = 0;
   @timeData = gmtime(time);
   $timeData[5] = $timeData[5] + 1900;
    if ($timeData[3] < 10) {
       $timeData[3] = "0" . $timeData[3];
       }
    if ($timeData[4] < 10) {
       $timeData[4] = "0" . $timeData[4];
       }

   $file_date = "_$timeData[4]$timeData[3]_$timeData[2]$timeData[1]";

   foreach $argnum (0 .. $#ARGV) {
      given ($ARGV[$argnum]) {
	 when (-help)        { &print_help; }
	 when (-numbers)     { print "[code2fig.pl]: -n switch found: add numbers to listing\n"; $numbers=1; }
	 when (-n)           { print "[code2fig.pl]: -n switch found: add numbers to listing\n"; $numbers=1; }
	 default             { $code_file = $ARGV[$argnum];}
	 }  
      }
   }

#------------------------------------------------------------------------------
sub find_basename {
   print "[code2fig.pl]: getting basename\n";

   $home = $ENV{HOME};
   $basename  = $code_file;
   $basename  =~ s/\.sv$//;
   $basename  =~ s/\.v$//;
   $basename  =~ s/\.txt$//;

   $current_directory = $ENV{PWD};
   # $current_directory =~ s/.*\///;
   $fail_file       = $current_directory . "/" . $basename . "_fail.sv";
   $transcript_file = $basename . ".log";
   $fig_file        = $current_directory . "/" . $basename . ".fig";
   $lyx_file        = $current_directory . "/" . $basename . ".lyx";
 
}

#------------------------------------------------------------------------------
sub read_in_code {
   if (-e $fail_file) {
      $command = "diff $code_file $fail_file";
      system($command);
      print "[code2fig.pl]: read in code file $fail_file \n";
      open code_file_handle, $fail_file or die "cannot open $fail_file for read :$!";
   } else {
      print "[code2fig.pl]: No FAIL file\n";
      print "[code2fig.pl]: read in code file $code_file \n";
      open code_file_handle, $code_file or die "cannot open $code_file for read :$!";
   }

   @code_file_array = <code_file_handle>;
   chop(@code_file_array);
   close(code_file_handle);
   $code_file_array_size = @code_file_array;
}

#------------------------------------------------------------------------------
sub read_in_transcript {
   if (-e $transcript_file) {
      print "[code2fig.pl]: read in transcript file $transcript_file \n";
      $command = "dos2unix $transcript_file";
      system($command);
      open transcript_file_handle, $transcript_file or die "cannot open transcript_file_array for read :$!";
      @transcript_file_array = <transcript_file_handle>;
      chop(@transcript_file_array);
      close(transcript_file_handle);
      $transcript_file_array_size = @transcript_file_array;
   } else {
      print "[code2fig.pl]: THERE IS NO $transcript_file\n";
   }
}

#------------------------------------------------------------------------------
sub add_transcript {
   if (-e $transcript_file) {
      print "[code2fig.pl]: writing transcript to figure\n";
      
      $write_out_transcript = 0;
      $max_x = 0;
      $transcript_title_y_dimension = $end_box_y + 180;
      print XFIG "4 0 0 40 -1 22 12 0.0000 6 210 1065 2340 $transcript_title_y_dimension Transcript\\001\n";

      for ($k = 0; $k < $transcript_file_array_size; $k++) {
         
         $y_dimension = (135 * $k) + $end_box_y;
         if ($write_out_transcript == 0 ) {
	    if ($transcript_file_array[$k] =~ / do do.tcl/) {
               $start_box_y   = $y_dimension - 90;
	       $write_out_transcript = 1;
               next;
	    } else {
               next;
	    }
	 }

         if ($transcript_file_array[$k] =~ /svdrop.source/) {
            next;
         }

         if (length($transcript_file_array[$k]) > $max_x) {
            $max_x = length($transcript_file_array[$k]);
         }
         
        	 
         $transcript_file_array[$k] =~ s/\#\s*//;
         $transcript_file_array[$k] =~ s///;
	 $xfig_transcript_string   = "4 0 0 40 -1 14 8 0.0000 6 90 825 2385 $y_dimension $transcript_file_array[$k] \\001";

	 print XFIG $xfig_transcript_string, "\n";
      }

      $end_box_y = $y_dimension + 90;
      $end_box_x   = $start_box_x + ($max_x * 80);
      $current_layer = $current_layer - 2;
      $start_box_x = 2305;

   } 
}

#------------------------------------------------------------------------------
sub parse_code {

   $j = 0;

   $start_box_y = 160;
   $max_x = 0;
   $current_layer = 48;
   $start_box_x = 2565;

   for ($k = 0; $k < $code_file_array_size; $k++) {

      $_ = $code_file_array[$k];
      s///g;
      
      # routine for printing a box around a piece of code, 
      # assuming that it find xerenetbox in the code
      if (/xerenetbox/) {
	 &place_box;
	 $current_layer = $current_layer - 2;
	 $start_box_y   = $end_box_y - 20;
      }

      if (/xereneton/) {
         $skip = 0;
      }

      if (/xerenetoff/) {
         $skip = 1;
      }

      if ($skip == 1) {
         next;
      } 

      &rip_comments;

      # if the line is just a comment, then skip it.
      if (/^\s*\/\/.*/) {
         $comment_only_line = $comment_only_line  + 1;
         s/\/\///;
         s/^\s*//;
         $comment_only_line_y_dimension = $k * 135;
         $xfig_comment_string_normal = "4 0 0 40 -1 22 12 0.0000 6 90 825 10385 $comment_only_line_y_dimension $_ \\001";
	 print XFIG $xfig_comment_string_normal , "\n";
         # print LYX_OUT " \\begin_layout Itemize\n $_\n \\end_layout\n\n";
	 next;
      } else {
	 $j++;
      }
	 
      # rip out comments, and escape backslashes, forward slashes and ampersands
      &cleanup_code;

      &fix_box_dimensions;

      if ($numbers == 1) {
	    $line_number = " $j  ";
	 if ($j < 1000) {
	    $line_number = " " . $line_number
         }
	 if ($j < 100) {
	    $line_number = " " . $line_number
         }
	 if ($j < 10) {
	    $line_number = " " . $line_number
         }
      } else {
	 $line_number = "";
      }
      
      $comment =~ s/^\s*//;

      $comment_string   = "4 0 0 40 -1 22 12 0.0000 6 120 1410 8010 $y_dimension $comment\\001";

      $xfig_code_string_normal = "4 0 0 40 -1 12 8 0.0000 6 90 825 2385 $y_dimension " . $line_number . "$code_file_array[$k] \\001";
      $xfig_code_string_bold   = "4 0 0 40 -1 14 8 0.0000 6 90 825 2385 $y_dimension " . $line_number . "$code_file_array[$k] \\001";

      if (length($comment) > 1) {
	 print XFIG $xfig_code_string_bold , "\n";
	 print XFIG $comment_string , "\n";
      } else {
	 print XFIG $xfig_code_string_normal , "\n";
      }
   }
}


# -----------------------------------------------------------------------------
sub close_xfig_file {
   close(XFIG);
}

# -----------------------------------------------------------------------------
sub print_help {

print << "HELP";

This script adds code to an xfig file (.fig).
Usage: code2fig.pl -n|-numbers|-help <code_file> 


HELP

die "Please re-run without the -help switch\n\n";

}

# -----------------------------------------------------------------------------
sub rip_comments {
   ($code,$comment) = split(/\/\//,$code_file_array[$k]);
   if (/xerenetbox/) {
      $comment = "";
   } 

   $code_file_array[$k] = $code;
   $comment =~ s/\/\/[ 	]*//g; # delete all comments
}


# -----------------------------------------------------------------------------
sub place_box {
print XFIG qq~
2 2 0 1 0 7 $current_layer -1 20 0.000 0 0 -1 0 0 5
             $start_box_x $start_box_y $end_box_x  $start_box_y $end_box_x $end_box_y $start_box_x $end_box_y $start_box_x $start_box_y
~;
}

# -----------------------------------------------------------------------------
sub fix_box_dimensions {
    # routine for working out the x and y box coordinates
    if (length($code_file_array[$k]) > $max_x) {
       $max_x = length($code_file_array[$k]);
    }
    $y_dimension =  (270 + (135*$j));
    $end_box_y   = $y_dimension + 90;
    $end_box_x   = $start_box_x + ($max_x * 80);
}

# -----------------------------------------------------------------------------
sub cleanup_code {
    $code_file_array[$k] =~ s/\/\/.*//g;   # delete all comments
    $code_file_array[$k] =~ s/\\n/\\\\n/g; # convert all newlines to newlines that PERL can print
    $code_file_array[$k] =~ s/\\/\\\\/g;   # convert all backslashes to backslashes that PERL can print
    $code_file_array[$k] =~ s/\//\\\//g;   # convert all forwardslashes to forwardslashes that PERL can print
    $code_file_array[$k] =~ s/&/\\&/g;     # Make sure that ampersands are escaped. (Is that necessary anymore, because we're not using a sedscript).
}

# -----------------------------------------------------------------------------
sub create_xfig_header {

   print "[code2fig.pl]: creating xfig figure: xxfig $fig_file \n";

open XFIG, ">$fig_file" or die "[code2fig.pl]: Can't open $fig_file for writing\n";
print XFIG "\#FIG 3.2  Produced by xfig version 3.2.5";
print XFIG qq~
Landscape
Center
Metric
A4      
100.00
Single
-2
1200 2
0 32 #ff0000
0 33 #bf3030
0 34 #a60000
0 35 #ff4040
0 36 #ff7373
0 37 #ff7400
0 38 #bf7130
0 39 #a64b00
0 40 #ff9640
0 41 #ffb273
0 42 #009999
0 43 #1d7373
0 44 #006363
0 45 #33cccc
0 46 #5ccccc
0 47 #00cc00
0 48 #269926
0 49 #008500
0 50 #39e639
0 51 #67e667
0 52 #ffff00
0 53 #bfbf30
0 54 #a6a600
0 55 #ffff40
0 56 #ffff73
0 57 #7109aa
0 58 #5f2580
0 59 #48036f
0 60 #9f3ed5
0 61 #ad66d5
0 62 #111111
0 63 #222222
0 64 #333333
0 65 #444444
0 66 #555555
0 67 #666666
0 68 #777777
0 69 #888888
0 70 #999999
0 71 #aaaaaa
0 72 #bbbbbb
0 73 #cccccc
0 74 #dddddd
0 75 #eeeeee
0 76 #3216b0
0 77 #3d2d84
0 78 #1b0773
0 79 #644ad8
0 80 #8370d8
0 81 #0f4da8
0 82 #284b7e
0 83 #052f6d
0 84 #437dd4
0 85 #6a94d4
~;

}

#------------------------------------------------------------------------------
sub print_lyx_header {

print LYX_OUT qq~
#LyX 1.6.7 created this file. For more info see http://www.lyx.org/
\\lyxformat 345
\\begin_document
\\begin_header
\\textclass extarticle
\\begin_preamble
\\date{}
\\def\\bstrut{\\vrule height2.5ex width0pt}
\\def\\pstrut{\\vrule height0.9ex width0pt}
\\def\\estrut{\\vrule depth.75ex width0pt}
\\end_preamble
\\use_default_options false
\\language english
\\inputencoding auto
\\font_roman default
\\font_sans default
\\font_typewriter default
\\font_default_family default
\\font_sc false
\\font_osf false
\\font_sf_scale 100
\\font_tt_scale 100

\\graphics default
\\paperfontsize 20
\\spacing single
\\use_hyperref true
\\pdf_bookmarks true
\\pdf_bookmarksnumbered true
\\pdf_bookmarksopen true
\\pdf_bookmarksopenlevel 4
\\pdf_breaklinks false
\\pdf_pdfborder true
\\pdf_colorlinks false
\\pdf_backref false
\\pdf_pdfusetitle true
\\papersize a4paper
\\use_geometry false
\\use_amsmath 0
\\use_esint 0
\\cite_engine basic
\\use_bibtopic false
\\paperorientation landscape
\\leftmargin 1cm
\\topmargin 3cm
\\rightmargin 1cm
\\bottommargin 1cm
\\headheight 1cm
\\headsep 1cm
\\footskip 0cm
\\secnumdepth 2
\\tocdepth 2
\\paragraph_separation indent
\\defskip medskip
\\quotes_language english
\\papercolumns 1
\\papersides 2
\\paperpagestyle default
\\bullet 1 0 15 -1
\\tracking_changes false
\\output_changes false
\\author "" 
\\author "" 
\\end_header

\\begin_body

\\begin_layout BeginSlide
Title
\\begin_inset CommandInset label
LatexCommand label
name "slide:label-should-be-the-same-as-slide-title"

\\end_inset


\\end_layout

\\begin_layout BeginSmall

\\end_layout

\\begin_layout Standard
\\begin_inset Float figure
wide false
sideways false
status open

\\begin_layout Plain Layout
\\begin_inset Graphics
	filename $fig_file
	scale 9169

\\end_inset


\\end_layout

\\begin_layout Plain Layout
\\begin_inset Caption

\\begin_layout Plain Layout
Simple example
\\end_layout

\\end_inset


\\begin_inset CommandInset label
LatexCommand label
name "figure:descriptive-label-for-diagram"

\\end_inset


\\end_layout

\\end_inset


\\end_layout

\\begin_layout BeginMakeNote
Notes
\\end_layout


~;


}

#------------------------------------------------------------------------------
sub print_lyx_footer {

print LYX_OUT qq~
\\begin_layout EndSmall

\\end_layout

\\begin_layout EndMakeNote

\\end_layout

\\begin_layout EndSlide

\\end_layout

\\begin_layout Standard
\\begin_inset Note Note
status open

\\begin_layout Plain Layout
\\begin_inset Tabular
<lyxtabular version="3" rows="3" columns="1">
<features>
<column alignment="left" valignment="top" width="0">
<row>
<cell alignment="left" valignment="top" usebox="none">
\\begin_inset Text

\\begin_layout Plain Layout
LRM: 
\\end_layout

\\end_inset
</cell>
</row>
<row>
<cell alignment="left" valignment="top" usebox="none">
\\begin_inset Text

\\begin_layout Plain Layout
Comment: 
\\end_layout

\\end_inset
</cell>
</row>
<row>
<cell alignment="center" valignment="top" usebox="none">
\\begin_inset Text

\\begin_layout Plain Layout
Author: mjones
\\end_layout

\\end_inset
</cell>
</row>
</lyxtabular>

\\end_inset


\\end_layout

\\end_inset


\\end_layout

\\end_body
\\end_document
~;
close(LYX_OUT);
}
