function [ppt] = createPresentation(savePath, saveName, title)

% Author: James Ives | james.white1@bbk.ac.uk / james.ernest.ives@gmail.com
% Date: 6th November 2021
% Released under GNU GPL v3.0: https://www.gnu.org/licenses/gpl-3.0.html
% Open to collaboration—feel free to contact me!

% Note, if you don't close the presentation then it won't save you can save
% it with close(ppt);

% Create a presentation
import mlreportgen.ppt.*

if nargin < 3
    title = saveName;
end

ppt = Presentation(strcat(savePath, '/', saveName, ".pptx"));
open(ppt);

% Add a slide to the presentation
slide = add(ppt,"Title and Content");

% Add title to the slide
replace(slide,"Title",title);

end