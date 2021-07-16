#ifndef RBTREE_H_OCT_06_2008
#define RBTREE_H_OCT_06_2008

#include <iostream>
using namespace std;
#include <cassert>
#include <cstdlib>

//RBNodes are also linked as a list
template<typename Type, typename Comp>
class RBTree
{
 //inner class
 public:
  class RBNode
  {
   public:
    RBNode() : red_(true), prev_(NULL), next_(NULL)
               { link_[0] = NULL; link_[1] = NULL; }
    RBNode(Type data) : red_(true), data_(data), prev_(NULL), next_(NULL)
                        { link_[0] = NULL; link_[1] = NULL; }
    ~RBNode() {}

    bool isRed() const        { return red_;     }
    Type data() const         { return data_;    }
    RBNode* leftLink() const  { return link_[0]; }
    RBNode* rightLink() const { return link_[1]; }
    RBNode* prev() const      { return prev_;    }
    RBNode* next() const      { return next_;    }

    RBNode* nextNode(const bool& forward)
    { if (forward) return next_; return prev_; }

    bool red_;
    Type data_;
    RBNode* link_[2];
    RBNode* prev_;
    RBNode* next_;
  };

 //RBTree definition
 public:
  RBTree() : minNode_(NULL), maxNode_(NULL), head_(NULL), tail_(NULL),
             root_(NULL), numItems_(0) {}
  ~RBTree()
  {
    RBNode* it = root_;
    RBNode* save;
    while (it != NULL)
    {
      if (it->link_[0] != NULL)
      {
          //Right rotation
        save = it->link_[0];
        it->link_[0] = save->link_[1];
        save->link_[1] = it;
      }
      else
      {
        save = it->link_[1];
        delete it;
      }
      it = save;
    }
  }


  RBNode* minNode() const            { return minNode_; }
  RBNode* maxNode() const            { return maxNode_; }
  void setMinNode(RBNode* const & n) { minNode_ = head_ = n; }
  void setMaxNode(RBNode* const & n) { maxNode_ = tail_ = n; }
  RBNode* head() const               { return head_; }
  RBNode* tail() const               { return tail_; }
  RBNode* root() const               { return root_; }
  int numItems() const               { return numItems_; }
  int size() const                   { return numItems_; }
  bool empty() const                 { return numItems_ == 0; }
  bool isRed(const RBNode* const & n) const { return n != NULL && n->red_; }
  void setRoot(RBNode* const & n)    { root_ = n; }
  void setNumItems(const int& num)   { numItems_ = num; }

  //this is a temporary removal; restore must be called later
  void tmpRemoveFromList(RBNode* const & n)
  {
    if (n->prev_) n->prev_->next_ = n->next_;
    if (n->next_) n->next_->prev_ = n->prev_;
    if (n == head_) head_ = n->next_;
    if (n == tail_) tail_ = n->prev_;
  }

  void restoreToList(RBNode* const & n)
  {
    if (n->prev_) n->prev_->next_ = n;
    if (n->next_) n->next_->prev_ = n;
    if (n->next_ == head_) head_ = n;
    if (n->prev_ == tail_) tail_ = n;
  }

  RBNode* single(RBNode* const & root, const int& dir)
  {
    RBNode* save = root->link_[!dir];

    root->link_[!dir] = save->link_[dir];
    save->link_[dir] = root;

    root->red_ = true;
    save->red_ = false;

    return save;
  }

  RBNode* ddouble(RBNode* const & root, const int& dir )
  {
    root->link_[!dir] = single(root->link_[!dir], !dir);
    return single(root, dir);
  }

  bool contains(Type data)
  {
    Type noop; RBNode* noop2;
    return find(data, noop, noop2);
  }

  bool find(Type data, Type& data2) const
  {
    RBNode* node;
    return find(data, data2, node);
  }

  bool find(Type data, Type& data2, RBNode*& node) const
  {
    RBNode* it = root_;
    node = NULL;

    while (it != NULL)
    {
      int cp = Comp::compare(it->data_,data);
      if (cp == 0) { data2 = it->data_; node = it; return true;}
      else
      {
        int dir = (cp < 0);
        it = it->link_[dir];
      }
    }

    return false;
  }

  bool insert(Type data) { RBNode* noop;  return insert(data, noop); }

  //returns true if insert occurred; false if data already in tree
  //if return true, retNode is new node; else retNode is existing node
  bool insert(Type data, RBNode*& retNode)
  {
    bool inserted = true;
    retNode = NULL;

    if (root_ == NULL)
    {
        //empty tree case
      root_ = new RBNode(data);
      if (root_==NULL) { cout<<"ERROR: failed to alloc root_;"<<endl; exit(-1);}
      //if (root_ == NULL) return false;
      retNode = root_;
      setMinNode(root_);
      setMaxNode(root_);
      numItems_++;
    }
    else
    {
      RBNode head; head.red_ = false; // false tree root
      RBNode * g, * t;  // grandparent & parent
      RBNode * p, * q;  // iterator & parent
      int dir = 0, last = 0;

      // set up helpers
      t = &head;
      g = p = NULL;
      q = t->link_[1] = root_;

      //search down the tree
      for ( ; ; )
      {
        if (q == NULL)
        {
            //insert new node at the bottom
          p->link_[dir] = q = new RBNode(data);
          if (q==NULL) { cout<<"ERROR: failed to alloc q;"<<endl; exit(-1);}
          //if (q == NULL) return false;
          retNode = q;

          numItems_++;
          if (Comp::compare(q->data_,minNode_->data_) < 0)      setMinNode(q);
          else if (Comp::compare(q->data_,maxNode_->data_) > 0) setMaxNode(q);

          if (dir == 0) //if q is less than p
          {
            q->next_ = p;
            q->prev_ = p->prev_;
            if (p->prev_) p->prev_->next_ = q;
            p->prev_ = q;
          }
          else // q is greater than p
          {
            q->prev_ = p;
            q->next_ = p->next_;
            if (p->next_) p->next_->prev_ = q;
            p->next_ = q;
          }
            //check no duplicates
          if (q->prev_) assert(Comp::compare(q->data_,q->prev_->data_) != 0);
          if (q->next_) assert(Comp::compare(q->data_,q->next_->data_) != 0);
        }
        else
        if ( isRed(q->link_[0]) && isRed(q->link_[1]) )
        {
           // color flip
          q->red_ = true;
          q->link_[0]->red_ = false;
          q->link_[1]->red_ = false;
        }

          //fix red violation
        if (isRed(q) && isRed(p))
        {
          int dir2 = (t->link_[1] == g);

          if (q == p->link_[last])
            t->link_[dir2] = single(g, !last);
          else
            t->link_[dir2] = ddouble(g, !last);
        }

          // stop if found
        int cp = Comp::compare(q->data_,data);
        if (cp == 0)
        {
          if (retNode == NULL) { inserted = false; retNode = q; }
          break;
        }

        last = dir;
        dir = (cp < 0);

          //update helpers
        if (g != NULL)  t = g;
        g = p, p = q;
        q = q->link_[dir];
      }

      //update root
      root_ = head.link_[1];
    }

    //make root black
    root_->red_ = false;

    return inserted;
  }//insert()

  bool remove(Type data) { Type noop; return remove(data, noop); }

  bool remove(Type data, Type& data2)
  {
    bool found = false;
    if (root_ != NULL )
    {
      RBNode head; head.red_ = false; //false tree root
      RBNode* q, * p, * g; //helpers
      RBNode* f = NULL;    //found item
      int dir = 1;

      //set up helpers
      q = &head;
      g = p = NULL;
      q->link_[1] = root_;

       //search and push a red down
      while ( q->link_[dir] != NULL )
      {
        int last = dir;
          //update helpers
        g = p, p = q;
        q = q->link_[dir];
        int cp = Comp::compare(q->data_,data);
        dir = (cp < 0);

          //save found node
        if (cp == 0)  f = q;

          //push the red node down
        if (!isRed(q) && !isRed(q->link_[dir]))
        {
          if (isRed(q->link_[!dir]))
            p = p->link_[last] = single(q, dir);
          else
          if (!isRed(q->link_[!dir]))
          {
            RBNode* s = p->link_[!last];

            if (s != NULL)
            {
              if (!isRed(s->link_[!last]) && !isRed(s->link_[last]))
              {
                  //color flip
                p->red_ = false;
                s->red_ = true;
                q->red_ = true;
              }
              else
              {
                int dir2 = (g->link_[1] == p);

                if (isRed(s->link_[last]))
                  g->link_[dir2] = ddouble(p, last);
                else
                if (isRed(s->link_[!last]))
                  g->link_[dir2] = single(p, last);

                //ensure correct coloring
                q->red_ = g->link_[dir2]->red_ = true;
                g->link_[dir2]->link_[0]->red_ = false;
                g->link_[dir2]->link_[1]->red_ = false;
              }
            }
          }
        }
      }

        //replace and remove if found
      if (f != NULL)
      {
        found = true;
        data2 = f->data_;

        f->data_ = q->data_;
        p->link_[p->link_[1] == q]  =  q->link_[q->link_[0] == NULL];

        if (f == q)
        {
          if (f->next_) f->next_->prev_ = f->prev_;
          if (f->prev_) f->prev_->next_ = f->next_;
          if (f == minNode_)      { setMinNode(f->next_); assert(!f->prev_); }
          else if (f == maxNode_) { setMaxNode(f->prev_); assert(!f->next_); }
        }
        else
        if (q->next_ == f)
        {
          assert(f->prev_ == q);
          f->prev_ = q->prev_;
          if (q->prev_) q->prev_->next_ = f;
          if (q == minNode_) setMinNode(f);
        }
        else
        if (q->prev_ == f)
        {
          assert(f->next_ == q);
          f->next_ = q->next_;
          if (q->next_) q->next_->prev_ = f;
          if (q == maxNode_) setMaxNode(f);
        }
        else
        {
          cout << "ERR: bad f and q position!" << endl;
          assert(false);
        }

        numItems_--;

        delete q;
      }

      // update root and make it black
      root_ = head.link_[1];
      if (root_ != NULL)
        root_->red_ = false;
    }

    return found;
  }//remove()

 public:
  void print(ostream& out) const { print(out, root_, 0); }

  int aassert(RBNode* const & root)
  {
    int lh, rh;

    if ( root == NULL ) return 1;

    RBNode* ln = root->link_[0];
    RBNode* rn = root->link_[1];

      //consecutive red links
    if (isRed(root))
    {
      if (isRed(ln) || isRed(rn))
      {
        cout << "ASSERT ERROR: Red violation" << endl;
        return 0;
      }
    }

    lh = aassert(ln);
    rh = aassert(rn);

      //invalid binary search tree
    if (   (ln != NULL && Comp::compare(ln->data_, root->data_) >= 0)
        || (rn != NULL && Comp::compare(rn->data_, root->data_) <= 0) )
    {
      cout << "ASSERT ERROR: Binary tree violation" << endl;
      return 0;
    }

    // black height mismatch
    if ( lh != 0 && rh != 0 && lh != rh )
    {
      cout << "ASSERT ERROR: Black violation" << endl;
      return 0;
    }

      //only count black links
    if ( lh != 0 && rh != 0 )
      return isRed(root) ? lh : lh + 1;

    return 0;
  }

 private:
  void print(ostream& out, const RBNode* const & root, const int& level) const
  {
    if (root == NULL)
    {
      for (int i = 0; i < level; i++ )
        out << '\t';
      out << "~" << endl;;
    }
    else
    {
      print(out, root->link_[1], level + 1);

      for (int i = 0; i < level; i++ )
        out << '\t';
      out << root->data() << endl;

      print(out, root->link_[0], level + 1);
    }
  }

 private:
  RBNode* minNode_;
  RBNode* maxNode_;
  RBNode* head_;
  RBNode* tail_;
  RBNode* root_;
  int numItems_;
};


#endif
