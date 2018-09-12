#import <iostream.h>

void hello() 
{
	TFile hdfile(infolder+prefix+"_hd.root","UPDATE");

	hits = hdfile->Get("hits");

	hits.Draw("hit_strip>>hhitsB");
	hhits = R.gPad.GetPrimitive("hhitsB");
	hhits.Fit("gaus");
	f1 = hhits.GetFunction("gaus");
	p0 = f1.GetParameter(0);
	p1 = f1.GetParameter(1);
	p2 = f1.GetParameter(2);
	hits_chi2 = f1.GetChisquare();

	lostrip = 7;
	histrip = 8;
	//print lostrip, histrip
}

