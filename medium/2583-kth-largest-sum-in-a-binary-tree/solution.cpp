// 2583. Kth Largest Sum in a Binary Tree
// https://leetcode.com/problems/kth-largest-sum-in-a-binary-tree/
//
// Difficulty: Medium
// Language:   C++
// Runtime:    10 ms (beats 99.73%)
// Memory:     157.5 MB (beats 100.00%)
// Submitted:  2024-10-22
// Submission: https://leetcode.com/submissions/detail/1430292268/
//
// ------------------------------------------------------------
//
// You are given the root of a binary tree and a positive integer k.
//
// The level sum in the tree is the sum of the values of the nodes that are on the same level.
//
// Return the k^th largest level sum in the tree (not necessarily distinct). If there are fewer than k
// levels in the tree, return -1.
//
// Note that two nodes are on the same level if they have the same distance from the root.
//
// Example 1:
//  [image: https://assets.leetcode.com/uploads/2022/12/14/binaryytreeedrawio-2.png]
//
// Input: root = [5,8,9,2,1,3,7,4,6], k = 2
// Output: 13
// Explanation: The level sums are the following:
// - Level 1: 5.
// - Level 2: 8 + 9 = 17.
// - Level 3: 2 + 1 + 3 + 7 = 13.
// - Level 4: 4 + 6 = 10.
// The 2^nd largest level sum is 13.
//
// Example 2:
//  [image: https://assets.leetcode.com/uploads/2022/12/14/treedrawio-3.png]
//
// Input: root = [1,2,null,3], k = 1
// Output: 3
// Explanation: The largest level sum is 3.
//
// Constraints:
//
// - The number of nodes in the tree is n.
// - 2 <= n <= 10^5
// - 1 <= Node.val <= 10^6
// - 1 <= k <= n

/**

 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
 using namespace std;
#include <vector>
#include <queue>
class Solution {
public:
    long long kthLargestLevelSum(TreeNode* root, int k) {
        vector<long long> sumyNaPoziomach;

        if(root==NULL){return -1;}
        queue<TreeNode*> q;

        q.push(root);


        while(!q.empty()){
            int  wielkoscPoz= q.size();
            long long pozVal =0;
            for(int i=0;i<wielkoscPoz;i++)
            {
                TreeNode* temp = q.front();
                q.pop();
                pozVal+=temp->val;
                if(temp->left!=NULL){q.push(temp->left);}
                if(temp->right!=NULL){q.push(temp->right);}
            }
            sumyNaPoziomach.push_back(pozVal);
        }
        

        sort(sumyNaPoziomach.begin(),sumyNaPoziomach.end(),greater<long long>());
        if(sumyNaPoziomach.size()<k)
        {
            return -1;
        }
        else{
            return sumyNaPoziomach[k-1];
        }


        
    }
};
