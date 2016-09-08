// get CMS SUSY analysis search region bin numbers
// takes kinematic observables as inputs

int JetsPlusMETSR(float mht, float ht, float njets, float nbjets) {
  // takes four main kinematic observables for CMS Multijet+MHT search
  // and returns search region number
  // analysis reference: http://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/SUS-16-014/index.html

  if (mht < 300 || ht < 300 || njets < 3 ) return -1; // not in any analysis bin

  // which interval in NJets ?
  // [3, 4]; [5,6]; [7,8] [9,inf)
  int inj(0);
  if (njets >= 5 && njets<=6) inj = 1;
  else if (njets >= 7 && njets<=8) inj = 2;
  else if (njets>=9) inj = 3;

  // which interval in mht?
  // [300, 350]; (350,500]; (500,750] (750,inf)
  int imht(0);
  if (mht > 350 && mht <= 500) imht = 1;
  else if (mht > 500 && mht <= 750) imht = 2;
  else if (mht > 750) imht = 3;

  // which interval in htmht?
  int ihtmht(0);
  switch (imht) {
  case 0:
    if (ht > 300 && ht <= 500) ihtmht = 0;
    else if (ht > 500 && ht <= 1000) ihtmht = 1;
    else if (ht > 1000) ihtmht = 2;
    break;
  case 1:
    if (ht > 350 && ht <= 500) ihtmht = 3;
    else if (ht > 500 && ht <= 1000) ihtmht = 4;
    else if (ht > 1000) ihtmht = 5;
    else return -1; // throw away event if ht < mht
    break;
  case 2:
    if (ht > 500 && ht <= 1000) ihtmht = 6;
    else if (ht > 1000) ihtmht = 7;
    else return -1; // throw away event if ht < mht
    break;
  case 3:
    if (ht > 750 && ht <= 1500) ihtmht = 8;
    else if (ht > 1500) ihtmht = 9;
    else return -1; // throw away event if ht < mht
    break;
  default:
    return -1;
  }

  return inj*40 + nbjets*10 + ihtmht + 1;
  
}
