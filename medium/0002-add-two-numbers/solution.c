// 2. Add Two Numbers
// https://leetcode.com/problems/add-two-numbers/
//
// Difficulty: Medium
// Language:   C
// Runtime:    2 ms (beats 43.58%)
// Memory:     12.7 MB (beats 99.81%)
// Submitted:  2025-02-27
// Submission: https://leetcode.com/submissions/detail/1557283725/
//
// ------------------------------------------------------------
//
// You are given two non-empty linked lists representing two non-negative integers. The digits are
// stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and
// return the sum as a linked list.
//
// You may assume the two numbers do not contain any leading zero, except the number 0 itself.
//
// Example 1:
//  [image: https://assets.leetcode.com/uploads/2020/10/02/addtwonumber1.jpg]
//
// Input: l1 = [2,4,3], l2 = [5,6,4]
// Output: [7,0,8]
// Explanation: 342 + 465 = 807.
//
// Example 2:
//
// Input: l1 = [0], l2 = [0]
// Output: [0]
//
// Example 3:
//
// Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
// Output: [8,9,9,9,0,0,0,1]
//
// Constraints:
//
// - The number of nodes in each linked list is in the range [1, 100].
// - 0 <= Node.val <= 9
// - It is guaranteed that the list represents a number that does not have leading zeros.

/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* addTwoNumbers(struct ListNode* l1, struct ListNode* l2) {
    
    struct ListNode* wynik = malloc(sizeof(struct ListNode));
    wynik->val = 0;
    wynik->next = NULL;
    int carry =0;
    struct ListNode* curr = wynik;
    while(l1 != NULL || l2!=NULL || carry !=0)
    {
        int dodawanie =0;
        (l1!=NULL) ? dodawanie+=l1->val : 0 ;
        (l2!=NULL) ? dodawanie+=l2->val : 0 ;
        dodawanie +=carry;
        carry = dodawanie /10;
        curr->next = malloc(sizeof(struct ListNode));
        curr->next->val = dodawanie % 10;
        curr->next->next = NULL;
          curr = curr->next;
        if (l1 != NULL) l1 = l1->next;
        if (l2 != NULL) l2 = l2->next;
    }

    struct ListNode* result = wynik->next;
    free(wynik);  
    return result;
}
