Subject:  $$00000001
Current Fact: :Andrew [Korean]
Type: Korean
Current Fact: :Korean >>Asian
Current Fact: :Korean #isBornInKorea
Current Fact: :Ichiro [Japanese]
Type: Japanese
Current Fact: :Japanese >>Asian
Current Fact: :Japanese #isBornInJapan
Current Fact: Andrew is male
Current Fact: Ichiro plays baseball
Current Fact: Ichiro hit 15 home runs in 2009
Current Fact: 

Entities are:
    Andrew
        Type is Korean 
         is male

    Ichiro
        Type is Japanese 
         plays baseball
         hit 15 home runs in 2009

    Japanese
         ['P', ':', 'Japanese', '>>Asian', [], '', '']
        Has a Restriction: 

    Korean
         ['P', ':', 'Korean', '>>Asian', [], '', '']
        Has a Restriction: 

Type Korean Has Parent: Asian
replacing previous parent of type Korean (  ) by Asian
Type Restrictions for Korean: isBornInKorea
Type Japanese Has Parent: Asian
replacing previous parent of type Japanese (  ) by Asian
Type Restrictions for Japanese: isBornInJapan
Set Type Info for:Korean
Set Type Info for:Japanese

Types and their Entities


t: Japanese
    res ['isBornInJapan']
Entities: Ichiro

t: Korean
    res ['isBornInKorea']
Entities: Andrew

Abstract Relations:


Relations Table:

    $$00000001 ismale <> is male
    $$00000002 playsbaseball <> plays baseball
    $$00000003 hithomerunsin <> hit () home runs ...

Relation Key Table:

    hit home runs in -->
        <> hit () home runs in ()
    is male         --> <> is male
    plays baseball  --> <> plays baseball

Relation Tag Table:

    hithomerunsin   --> <> hit () home runs in ()
    ismale          --> <> is male
    playsbaseball   --> <> plays baseball

Possible Vocabulary:

Korean     []
Japanese   []

*   <> hit () home runs in ()
*   <> is male
*   <> plays baseball
