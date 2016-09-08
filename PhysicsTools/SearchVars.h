// calculate CMS SUSY analysis kinematic variables
// from collections of jets (only TLorentzVector supported now)

#include "TVector2.h"
#include "TLorentzVector.h"

TVector2 MHTVec(std::vector<TLorentzVector> jets) {
  float mht_x(0.), mht_y(0.);
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>5.0) continue;
    mht_x -= jets[ijet].Px();
    mht_y -= jets[ijet].Py();
  }
  return TVector2(mht_x, mht_y);
}

float MHT(std::vector<TLorentzVector> jets) {
  TVector2 mht_vec(MHTVec(jets));
  return mht_vec.Mod();
}

float HT(std::vector<TLorentzVector> jets) {
  float ht(0.);
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>2.4) continue;
    ht += jets[ijet].Pt();
  }
  return ht;
}

float NJets(std::vector<TLorentzVector> jets) {
  int njets(0.);
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>2.4) continue;
    njets ++;
  }
  return njets;
}

bool PassDeltaPhiCut(std::vector<TLorentzVector> jets) {
  // evaluates whether or not event passes delta phi cut
  // used in CMS-PAS-SUS-16-014

  int njets = NJets(jets);
  if (njets<3) return false;

  TVector2 mht_vec(MHTVec(jets));
  
  // first, identify three-four leading jets
  int jet1(-1), jet2(-1), jet3(-1), jet4(-1);
  float pt_max(0.);
  // leading jet
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>2.4) continue;
    if (jets[ijet].Pt()>pt_max) {
      jet1 = ijet;
      pt_max = jets[ijet].Pt(); 
    }
  }
  if (jet1<0 || fabs(TVector2::Phi_mpi_pi(jets[jet1].Phi()-mht_vec.Phi())) < 0.5) return false;
  // subleading jet
  pt_max=0.;
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>2.4) continue;
    if (ijet==jet1) continue;
    if (jets[ijet].Pt()>pt_max) {
      jet2 = ijet;
      pt_max = jets[ijet].Pt(); 
    }
  }
  if (jet2 < 0 || fabs(TVector2::Phi_mpi_pi(jets[jet2].Phi()-mht_vec.Phi())) < 0.5) return false;
   // third-leading jet
  pt_max=0.;
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>2.4) continue;
    if (ijet==jet1 || ijet==jet2) continue;
    if (jets[ijet].Pt()>pt_max) {
      jet3 = ijet;
      pt_max = jets[ijet].Pt(); 
    }
  }
  if (jet3 < 0 || fabs(TVector2::Phi_mpi_pi(jets[jet3].Phi()-mht_vec.Phi())) < 0.3) return false; // note looser cut on 3rd-4th jets
  // in case of 3-jet event, we're done
  if (njets==3) return true;
   // fourth-leading jet
  pt_max=0.;
  for (unsigned ijet(0); ijet<jets.size(); ijet++) {
    if (jets[ijet].Pt()<30) continue;
    if (fabs(jets[ijet].Eta())>2.4) continue;
    if (ijet==jet1 || ijet==jet2 || ijet==jet3) continue;
    if (jets[ijet].Pt()>pt_max) {
      jet4 = ijet;
      pt_max = jets[ijet].Pt(); 
    }
  }
  if (jet4 < 0 || fabs(TVector2::Phi_mpi_pi(jets[jet4].Phi()-mht_vec.Phi())) < 0.3) return false; // note looser cut on 3rd-4th jets

  // if we've made it this far, event passes cut
  return true;
}
