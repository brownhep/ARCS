import ROOT as R
import math
import random

def simulate(title,loops,rad,collh,dsnsr,xstrip,pitch,noise,diffusion,steps):

   RFile = R.TFile("simulation.root","UPDATE")
   qdist = R.TProfile("qdistro_"+title, "Charge Distribution", 32,0,32)
   hdist = R.TH1I("hitdistro_"+title, "Hit Distribution", 32,0,32)
   heta = R.TH1F("eta_"+title, "Eta Distribution", 120,-0.1,1.1)
   source = R.TH2F("source_"+title,"source",100,-1,1,100,-1,1)

   for loop in xrange(loops):
	print title, loop
	pi = 3.14159
	phimax = math.atan(2*rad/collh)
	for i in xrange(steps):
		x = -rad + i*2*rad/steps
		ymin = math.sqrt(rad*rad - x*x)
		#print "Ymin ", ymin, x
		for j in xrange(int(steps*ymin/rad)):
			y = -ymin + j*2*rad/steps
			if rad*rad - x*x - y*y > 0:
				zmin = math.sqrt(rad*rad - x*x - y*y)
			else:
				zmin = 0
			for k in xrange(int(steps*zmin/rad)):
				z = -zmin + k*2*rad/steps
				#energy = getrdmE()
				source.Fill(x,y)
				#if (x*x + y*y + z*z) > rad*rad: continue
					#simulhit(x,y,z,9.5,steps)
				theta = 2*pi*random.random()
				phi = phimax*random.random()
				xh = x + collh*math.tan(phi)*math.cos(theta)
				yh = y + collh*math.tan(phi)*math.sin(theta)
				xt = x + (collh+dsnsr)*math.tan(phi)*math.cos(theta)
				#yt = y + (collh+dsnsr)*math.tan(phi)*math.sin(theta)
				xb = x + (collh+dsnsr+0.3)*math.tan(phi)*math.cos(theta)
				#yb = y + (collh+dsnsr+0.3)*math.tan(phi)*math.sin(theta)	
				if xb < xt: 
					#print "top"
					xbe = xb - diffusion/cos(phi)		
					xte = xt + diffusion/cos(phi)
				else:		
					#print "bot"
					xbe = xb + diffusion/cos(phi)	
					xte = xt - diffusion/cos(phi)
				xlt = xt - diffusion/cos(phi)
				xlb = xb - diffusion/cos(phi)
				xrt = xt + diffusion/cos(phi)
				xrb = xb - diffusion/cos(phi)
				for stp in range(int(xstrip+xbe/pitch),int(xstrip+xte/pitch)):
					print "a", stp, xstrip, int(xstrip+xbe/pitch), int(xstrip+xte/pitch), xbe, xte,diffusion
					a = 1
					pct = a*a*0.5/((a+b)*2*diffusion
				if (xh*xh + yh*yh) < rad: 
					#st_top = xstrip + xt/pitch
					#st_bot = xstrip + xb/pitch
					st_top = xstrip + xte/pitch
					st_bot = xstrip + xbe/pitch
					a = st_top - int(st_top)
					if int(xbe) != xt:
						pct_top = ((st_top - int(st_top))*pitch)/(xb-xt)
					#pct_top = ((st_top+1-xstrip)*pitch - xt)/(xb-xt)
					if xb > xt:
						pct_top = ((st_top - int(st_top))*pitch)/(xb-xt)
					else:
						pct_top = ((int(st_top) - st_top)*pitch)/(xb-xt)
					if abs(int(st_top)-int(st_bot)) > 1: print "3 strip event!!"
					if abs(pct_top)>1:  
						hdist.Fill(st_top)
						qdist.Fill(st_top,1)
						if xb > xt: 
							R1 = 1.0
							L1 = 0.0
							#heta.Fill(1)
						else: 
							R1 = 0.0
							L1 = 1.0
							#heta.Fill(0)
					else:
						qdist.Fill(st_top, pct_top)
						qdist.Fill(st_bot, 1-pct_top)
						#heta.Fill(pct_top)
						R1 = pct_top
						L1 = 1-pct_top
						if pct_top > 0.5: hdist.Fill(st_top)
						else: hdist.Fill(st_bot)
					R1 = addnoise(R1,noise)
					L1 = addnoise(L1,noise)
					eta = R1/(R1+L1)
					#print R1, L1, eta
					heta.Fill(eta)
					#elif pct_top<0:
					#	hdist.Fill(st_top, -1*pct_top)
					#	hdist.Fill(st_bot, 1+pct_top)						
					#if st_bot > st_top:
					#	pct_top = ((st_top+1-xstrip)*pitch - xt)/(xb-xt)
					#	hdist.Fill(st_top, pct_top)
					#	hdist.Fill(st_bot, 1-pct_top)
					#	#print pct_top
					#if st_bot == st_top:
					#	pct_top = ((st_top+1-xstrip)*pitch - xt)/(xb-xt)
					#	hdist.Fill(st_top, pct_top)
					#	hdist.Fill(st_bot, 1-pct_top)
					#	print pct_top
					#if st_top != st_bot: print x,y,z,xb, st_top, st_bot
 
   etapct = heta.Integral(30,89)/heta.Integral()
   print "Eta% ", etapct
   RFile.Write("",R.TObject.kOverwrite)
   RFile.Close()

def addnoise(signal,noise):
	newsig = signal - noise + 2*noise*random.random()
	return(newsig)

def simulhit(x,y,z,collh,steps):
	for i in xrange(steps):
		for j in xrange(steps):
			theta = 1
			phi = 1	


def getrdmE(par):
	#Fit parameters:
	#par[0]=Width (scale) parameter of Landau density
	#par[1]=Most Probable (MP, location) parameter of Landau density
	#par[2]=Total area (integral -inf to inf, normalization constant)
	#par[3]=Width (sigma) of convoluted Gaussian function

	mpshift  = -0.22278298
	mpc = par[1] - mpshift * par[0]
	fland = R.TMath.Landau(xx,mpc,par[0])/par[0]
	fgaus = R.TMath.Gaus(x[0],xx,par[3])
	flangaus = fland*fgaus
	return(1)


#print "loop ", i
simulate("70um",2,0.5,9.5,1.0,15,0.07,.07,0,100)
simulate("80um",2,0.5,9.5,1.0,15,0.08,.07,0,100)
simulate("120um",2,0.5,9.5,1.0,15,0.12,.07,0,100)
simulate("240um",2,0.5,9.5,1.0,15,0.24,.07,0,100)
