//#include <math.h>
//#include <stdio.h>

#include "TFile.h"
#include "TTree.h"
#include "TH1.h"
#include "TH2.h"
#include "TF1.h"
#include "TProfile.h"

void hello()
{
  	//for (int i = 0; i < times; i++)
  	//{
    	//	cout << "hello world!" << endl;
  	//}
   string hdf[1];
   hdf[0] = "./rootfiles/FTH200N_W4_R6_1samp/FTH200N_W4_closesr90_2ndrun_R6_hd.root";
   hdf[1] = "./rootfiles/FTH200Y_closesr90_R1/FTH200Y_closesr90_R1_hd.root";
   hdf[2] = "./rootfiles/FTH200Y_closesr90_R2/FTH200Y_closesr90_R2_hd.root";
   hdf[3] = "./rootfiles/FTH200Y_closesr90_R6/FTH200Y_closesr90_R6_hd.root";
   hdf[4] = "./rootfiles/FTH200Y_closesr90_R7/FTH200Y_closesr90_R7_b_hd.root";
   hdf[5] = "./rootfiles/FTH200Y_closesr90_R8/FTH200Y_closesr90_R8_hd.root";
   hdf[6] = "./rootfiles/FTH200Y_closesr90_R9/FTH200Y_closesr90_R9_hd.root";
   hdf[7] = "./rootfiles/FTH200N_W4_R5_1samp/FTH200N_W4_closesr90_1samp_R5_hd.root";
   //hdf[0] = "./rootfiles/FTH200N_W4_R5_1samp/FTH200N_W4_closesr90_1samp_R5_hd.root";
   for (int i = 0; i < 8; i++)
   {
	cout << "Opening " << hdf[i] << endl;

	switch (i):
	{
	case 0:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200N_W4_R6_1samp/FTH200N_W4_closesr90_2ndrun_R6_hd.root","UPDATE");
		break;
	case 1:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200Y_closesr90_R2/FTH200Y_closesr90_R2_hd.root","UPDATE");
		break;
	case 2:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200Y_closesr90_R6/FTH200Y_closesr90_R6_hd.root","UPDATE");
		break;
	case 3:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200Y_closesr90_R7/FTH200Y_closesr90_R7_b_hd.root","UPDATE");
		break;
	case 4:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200Y_closesr90_R8/FTH200Y_7_closesr90_LTR_R8_hd.root","UPDATE");
		break;
	case 5:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200Y_closesr90_R9/FTH200Y_closesr90_R9_hd.root","UPDATE");
		break;
	case 6:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200Y_closesr90_R1/FTH200Y_closesr90_R1_hd.root","UPDATE");
		break;
	case 7:
        	TFile *hdfile = TFile::Open("./rootfiles/FTH200N_W4_R5_1samp/FTH200N_W4_closesr90_R5_1samp_b_hd.root","UPDATE");
		break;
	}

        //TFile *hdfile = TFile::Open(hdf[i],"UPDATE");

        TTree *hits = hdfile->Get("hits");

        hits->Draw("hit_strip>>hhitsB");
        TH1F *hhits = gPad->GetPrimitive("hhitsB");
        hhits->Fit("gaus");
        TF1 *f1 = hhits->GetFunction("gaus");
        double p0 = f1->GetParameter(0);
        double p1 = f1->GetParameter(1);
        double p2 = f1->GetParameter(2);
        double hits_chi2 = f1->GetChisquare();
	hhits->Write("Hits",TObject::kOverwrite);

	cout << p0 << " " << p1-p2 << " " << p1+p2 << " " << hits_chi2 << endl;

	//int lostrip = int(round(p1 - p2));
	//int histrip = int(round(p1+p2));
	//int lostrip = int(0.5 + p1 - p2));
	//int histrip = int(0.5 + p1 + p2));
	double sigma = 0.68;
	int lostrip = int(0.5+p1-p2*sigma);
	int histrip = int(0.5+p1+p2*sigma);
	TString cut1 = Form("hit_strip>=%d && hit_strip<=%d", lostrip, histrip);
	TString cut2 = Form("hit_strip<%d || hit_strip>%d", lostrip, histrip);
	cout << lostrip << " " << histrip << " " << cut1 << " " << cut2 << endl;

	TH2F *hseed0 = new TH2F("hseed0","Seed0",255,0,255,1000,0,100);
	hits->Project("hseed0","strip_charge:runno", cut1);
	TProfile *hprof0 = hseed0->ProfileX();
	hprof0->Draw();
	hprof0->Write("SeedMid",TObject::kOverwrite);

	TH2F *hseed1 = new TH2F("hseed1","Seed1",255,0,255,1000,0,100);
	hits->Project("hseed1","strip_charge:runno", cut2);
	TProfile *hprof1 = hseed1->ProfileX();
	hprof1->Draw();
	hprof1->Write("SeedOuter",TObject::kOverwrite);

	TH2F *hclust0 = new TH2F("hclust0","Clust0",255,0,255,1000,0,100);
	hits->Project("hclust0","clust_charge:runno", cut1);
	TProfile *hprof2 = hclust0->ProfileX();
	hprof2->Draw();
	hprof2->Write("ClustMid",TObject::kOverwrite);

	TH2F *hclust1 = new TH2F("hclust1","Clust1",255,0,255,1000,0,100);
	hits->Project("hclust1","clust_charge:runno", cut2);
	TProfile *hprof3 = hclust1->ProfileX();
	hprof2->Draw();
	hprof2->Write("ClustOuter",TObject::kOverwrite);

	TH2F *heta0 = new TH2F("heta0","Eta0",255,0,255,1000,0,100);
	hits->Project("heta0","abs(eta-0.5):runno", cut1);
	TProfile *hprof4 = heta0->ProfileX();
	hprof4->Draw();
	hprof4->Write("EtaMid",TObject::kOverwrite);

	TH2F *heta1 = new TH2F("heta1","Eta1",255,0,255,1000,0,100);
	hits->Project("heta1","abs(eta-0.5):runno", cut2);
	TProfile *hprof5 = heta1->ProfileX();
	hprof5->Draw();
	hprof5->Write("EtaOuter",TObject::kOverwrite);

	TCanvas *c1 = new TCanvas("c1","Plots", 200, 10, 800, 1000);
	c1->Divide(1,3);
	c1->cd(1);
	hprof0->Draw();
	hprof1->SetLineColor(2);
	hprof1->Draw("same");
	c1->cd(2);
	hprof2->Draw();
	hprof3->SetLineColor(2);
	hprof3->Draw("same");
	c1->cd(3);
	hprof4->Draw();
	hprof5->SetLineColor(2);
	hprof5->Draw("same");

	c1->Write("Plots",TObject::kOverwrite);
	c1->Print("test.pdf");

	hdfile->Close();
   }
}
