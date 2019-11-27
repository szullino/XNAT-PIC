This is a tool which enables user to interact with an XNAT server through a GUI. It has three main functions:
1. Convert Bruker data to DICOM
2. Convert Aspect data to DICOM (not available yet)
3. Upload DICOM data to XNAT

When converting Bruker data to DICOM or uploading DICOM to XNAT the user can select a patient folder or a project folder which contains more patients with a structure like this:

project name
          |
          |_______patient name		
	  |		|______	1
	  |		|	|_______ Bruker data / Dicom data
	  |		|
          |		|_______2
	  |	  	|	|_______ Bruker data / Dicom data
	  |             |
          |
	  |_______patient name
	  |		|______	1
	  |		|	|_______ Bruker data / Dicom data
	  |		|
          |		|_______2
	  |	  	|	|_______ Bruker data / Dicom data
	  |             |		
          |

patient name
          |
          |_______1
	  |       |_______ Bruker data / Dicom data
          |
          |_______2
	  |	  |_______ Bruker data / Dicom data
          |
          |_______3
	  |       |_______ Bruker data / Dicom data

When uploading Dicom files to XNAT the user can also adopt a more complex structure that automatically sets custom variables (up to 3) and their values when uploading their experiments to XNAT. For example in this structure we have the following custom variables and corresponding custom values:

|-----------------------------------|
| custom variables | custom values  | 
|-----------------------------------|
| 	group      | 	treated     |
|		   |    untreated   |
|__________________|________________|
| 	           | 	pre         |
|    timepoint	   |    post1w      |
|		   |	post2w      |
|__________________|________________|

To set the above shown custom variables the folder hierarchy should match this example hierarchy:

project name
          |
 	  |_______group
		  |		
		  |_______treated
		  |	 |
         	  |	 |_______timepoint 
		  |      |	 |______ pre
		  |	 |       |          |_______ patient name
		  | 	 |	 |			  |
		  |	 | 	 |		          |___ 1 
		  |	 |	 |		          |    |_____ Dicom Data
		  | 	 |	 |			  |
	  	  |	 |	 |                        |____2
		  |	 |	 |			       |_____ Dicom Data
		  |      |	 |_______post1w
                  |      |       | 	       |____
          	  |	 	 |_______post2w
		  |		 |	       |____	
		  |
		  |______untreated
		  	 |
         	  	 |_______timepoint
          		 |	 |_____ pre
			 |		   |___


Before running, make sure your patient/full project structure matches this hierarchy.
