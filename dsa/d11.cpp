#include<iostream>
using namespace std;

vector<int>twosum(vector<int>&nums,int target){
    unordered_map<int,int>mp;
    vector<int>res;
    for(int i=0; i<nums.size(); i++){
        int comp = target - nums[i];
        if(mp.find(comp) != mp.end()){
            res.push_back(mp[comp]);
            res.push_back(i);
            return res;
        }
        mp[nums[i]] = i;
    }
    return res;

}
int main() {
    
    return 0;
}