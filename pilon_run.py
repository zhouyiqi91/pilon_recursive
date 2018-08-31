#This script is to run pilon automatically
import sys
import subprocess
import os
import configparser as cp
import glob

#bin_path
bin_path = os.path.abspath(__file__).strip("pilon_run.py")

#shell prefix
shell_prefix = "?export PERL5LIB=''\n?source activate pilon\n"

#config file
conf_file = sys.argv[1]
config = cp.ConfigParser()
config.read(conf_file)
infile = config["input_file"]
bwa = config["bwa"]
pilon = config["pilon"]

fastq_dir = infile["fastq_dir"]
fasta = infile["fasta"]
name = infile["name"]
run_mode = infile["run_mode"].strip()
iteration = int(infile["iteration"].strip())
genome_size = os.path.getsize(fasta)

bwa_cpu = bwa["cpu"]
bwa_queue = bwa["queue"]
bwa_opts = bwa["opts"].strip()
bwa_mem = int(genome_size/1073741824*3)
if bwa_mem < 5:
	bwa_mem = 5
bwa_mem = str(bwa_mem) + "G"

pilon_cpu = pilon["cpu"]
pilon_mem = pilon["memory"]
pilon_queue = pilon["queue"]
pilon_opts = pilon["opts"].strip()

base_dir = os.getcwd()

if 0 < iteration < 11:
	pass
else:
	exit("iteration should be in [1..10]!")



def run_once(out_dir,fastq_dir,fasta,name,run_mode,bwa_cpu,bwa_queue,bwa_opts,bwa_mem,pilon_cpu,pilon_mem,pilon_queue,pilon_opts):
	if run_mode in ["all","script"]:
		#bwa index
		os.chdir(out_dir)
		os.system("mkdir bwa")
		os.chdir("bwa")

		with open("index.sh",'w') as shell:
			shell.write(shell_prefix+"""ln -s """+fasta+""" """+name+""".fasta
bwa index """+name+""".fasta\n""")
		new_fasta = os.getcwd()+"/"+name+".fasta"

		#bwa mem
		read1s = glob.glob(fastq_dir+"/*_1*.fq") + glob.glob(fastq_dir+"/*_1*.fq.gz") 
#+ glob.glob(fastq_dir+"/*_1*.fastq") + glob.glob(fastq_dir+"/*_1*.fastq.gz")
		sorted_bams = []
		with open("align.sh",'w') as shell:
			shell.write(shell_prefix)
			for read1 in read1s:
				prefix = read1.split("/")[-1].split("_1")[0]
				read2 = (glob.glob(fastq_dir+"/"+prefix+"_2*.fq")+glob.glob(fastq_dir+"/"+prefix+"_2*.fq.gz"))[0]
				shell.write("""bwa mem -t """+str(bwa_cpu)+""" """+new_fasta+""" """+read1+""" """+read2+""" |samtools view -Sb - >"""+prefix+""".bam\n""")
				shell.write("""samtools sort """+prefix+""".bam """+prefix+"""_sort\n""")
				shell.write("""samtools index """+prefix+"""_sort.bam \n""")
				sorted_bams.append("./bwa/"+prefix+"_sort.bam")

	#pilon
		frags_line = ""
		for sorted_bam in sorted_bams:
			frags_line += " --frags "+sorted_bam
		pilon_line = "pilon -Xmx"+pilon_mem+" --diploid --changes --threads "+pilon_cpu+" --output "+name+" --genome "+new_fasta+frags_line
		os.chdir(out_dir)
		with open("pilon.sh",'w') as shell:
			shell.write(shell_prefix)
			shell.write(pilon_line+"\n")

		print ("scripts generated.")

#run
	if run_mode in ["all","submit"]:
		os.chdir(out_dir)
		os.chdir("bwa")
		#index
		if not os.path.exists("index_done"):
			cmd = "python "+bin_path+"sgearray.py -l vf="+bwa_mem+",p=1 -c 2 -q "+bwa_queue+" "+bwa_opts+" "+out_dir+"/bwa/index.sh"
			print (cmd)
			ret = subprocess.call(cmd,shell=True)
			if ret == 0:
				os.system("touch index_done")
			else:
				exit("index job failed")
		#align
		if not os.path.exists("align_done"):
			cmd = "python "+bin_path+"sgearray.py -l vf="+bwa_mem+",p="+str(bwa_cpu)+" -c 3 -q "+bwa_queue+" "+bwa_opts+" "+out_dir+"/bwa/align.sh"
			print (cmd)
			ret = subprocess.call(cmd,shell=True)
			if ret == 0:
				os.system("touch align_done")
			else:
				exit("align job failed")
		#pilon
		os.chdir(out_dir)
		if not os.path.exists("pilon_done"):
			cmd = "python "+bin_path+"sgearray.py -l vf="+pilon_mem+",p="+str(pilon_cpu)+" -c 1 -q "+pilon_queue+" "+pilon_opts+" "+out_dir+"/pilon.sh"
			print (cmd)
			ret = subprocess.call(cmd,shell=True)
			if ret == 0:
				os.system("touch pilon_done")
				print ("all pilon job done.")
			else:
				exit("pilon job failed")

	global next_fasta
	next_fasta = out_dir + "/" + name +".fasta" 

			
next_fasta = fasta
for run_time in range(1,iteration+1):
	new_out_dir = base_dir +"/"+str(run_time)
	os.mkdir(new_out_dir)
	run_once(out_dir=new_out_dir,fastq_dir=fastq_dir,fasta=next_fasta,name=name,run_mode=run_mode,bwa_cpu=bwa_cpu,bwa_queue=bwa_queue,bwa_opts=bwa_opts,bwa_mem=bwa_mem,pilon_cpu=pilon_cpu,pilon_mem=pilon_mem,pilon_queue=pilon_queue,pilon_opts=pilon_opts)
	if run_mode != "script":
		print ("iteration "+str(run_time) +" done.")



