// 21. Merge Two Sorted Lists
// https://leetcode.com/problems/merge-two-sorted-lists/
//
// Difficulty: Easy
// Language:   C#
// Runtime:    10 ms (beats 2.34%)
// Memory:     43.9 MB (beats 7.44%)
// Submitted:  2025-12-02
// Submission: https://leetcode.com/submissions/detail/1845356877/
//
// ------------------------------------------------------------
//
// You are given the heads of two sorted linked lists list1 and list2.
//
// Merge the two lists into one sorted list. The list should be made by splicing together the nodes of
// the first two lists.
//
// Return the head of the merged linked list.
//
// Example 1:
//  [image: https://assets.leetcode.com/uploads/2020/10/03/merge_ex1.jpg]
//
// Input: list1 = [1,2,4], list2 = [1,3,4]
// Output: [1,1,2,3,4,4]
//
// Example 2:
//
// Input: list1 = [], list2 = []
// Output: []
//
// Example 3:
//
// Input: list1 = [], list2 = [0]
// Output: [0]
//
// Constraints:
//
// - The number of nodes in both lists is in the range [0, 50].
// - -100 <= Node.val <= 100
// - Both list1 and list2 are sorted in non-decreasing order.

/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     public int val;
 *     public ListNode next;
 *     public ListNode(int val=0, ListNode next=null) {
 *         this.val = val;
 *         this.next = next;
 *     }
 * }
 */
public class Solution {
    public ListNode MergeTwoLists(ListNode list1, ListNode list2) {
        ListNode dummyHead = new ListNode();
        ListNode head = dummyHead;

        while(list1!=null || list2!=null){
            int val1= (list1==null) ? int.MaxValue : list1.val;
             int val2= (list2==null) ? int.MaxValue : list2.val;
             Console.WriteLine($"{val1} {val2}");
             if(val1<val2){
                head.next=list1;
                head=head.next;
                list1= list1.next;
             }
             else{
                head.next=list2;
                head=head.next;
                list2 =list2.next;
             }
        }


        return dummyHead.next;
    }
}
