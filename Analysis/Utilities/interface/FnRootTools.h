#ifndef ICHiggsTauTau_Utilities_FnRootTools_h
#define ICHiggsTauTau_Utilities_FnRootTools_h
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"

namespace ic {

  std::vector<std::vector<unsigned>> GenerateCombinations(std::vector<unsigned> vec);

  template <class T>
  T GetFromTFile(std::string const& filepath, std::string const& objectpath, std::string const& objectname) {
    TFile *file = new TFile(filepath.c_str());
    if (!file) {
      std::cerr << "Error: TFile \"" << filepath << "\" cannot be opened, an exception will be thrown" << std::endl;
      throw;
    }
    file->cd();
    gDirectory->cd(objectpath.c_str());

    T result = *(dynamic_cast<T*>(gDirectory->Get(objectname.c_str())));
    file->Close();
    return result;
  }

  template <class T>
  T GetFromTFile(TFile * file, std::string const& objectpath, std::string const& objectname) {
    if (!file) {
      std::cerr << "Error: TFile is not valid, an exception will be thrown" << std::endl;
      throw;
    }
    file->cd();
    gDirectory->cd(objectpath.c_str());
    T result = *(dynamic_cast<T*>(gDirectory->Get(objectname.c_str())));
    return result;
  }

  template <class T>
  T OpenFromTFile(std::string const& fullpath) {
    std::size_t pos = fullpath.find(':');
    std::string filepath = "";
    std::string objectpath = "";
    if (pos == std::string::npos || pos == 0 || pos == (fullpath.size() - 1)) {
      throw std::runtime_error("Input path must of the format file.root:object");
    } else {
      filepath = fullpath.substr(0, pos);
      objectpath = fullpath.substr(pos + 1);
    }
    TFile file(filepath.c_str());
    if (!file.IsOpen()) {
      throw std::runtime_error("File is invalid");
    }
    file.cd();
    T* obj_ptr = dynamic_cast<T*>(gDirectory->Get(objectpath.c_str()));
    if (!obj_ptr) {
      throw std::runtime_error("Object " + objectpath + " is missing or of wrong type");
    }
    return *obj_ptr;
  }

  std::vector<std::string> ParseFileLines(std::string const& file_name);

  template<class T>
  void SaveViaTree(TFile& file, T const& object, std::string name){
    T const* object_ptr = &object;
    file.cd();
    TTree* tree = new TTree(name.c_str(),name.c_str());
    tree->Branch(name.c_str(),&object_ptr);
    tree->Fill();
    tree->Write();
    delete tree;
  }

  template<class T>
  T LoadViaTree(TFile& file, std::string name){
    file.cd();
    TTree* tree = dynamic_cast<TTree*>(file.Get(name.c_str()));
    T* object_ptr = 0;
    tree->SetBranchAddress(name.c_str(),&object_ptr);
    tree->GetEntry(0);
    return (*object_ptr);
  }

  void VerticalMorph(TH1F *central, TH1F const*up, TH1F const*down, double shift);


} // namepsace
#endif
