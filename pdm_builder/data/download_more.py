import tarfile, shutil, os, requests

print "Please note that most of these images are not in the public domain. "
print "Using the images for training a model is considered 'transformative use' and thus 'fair use'. "
print "You are however, due to copyright, still not allowed to share or reproduce this set of images, publically or privately, in any way. "
print "Please respect these rules. Press any key to continue."
raw_input()

files = {
	"090312093916-large.jpg" : "http://images.sciencedaily.com/2009/03/090312093916-large.jpg",
	 "10142384-highly-detailed-fine-art-portrait-smiling-happy-real-person.jpg" : "http://us.123rf.com/400wm/400/400/warrengoldswain/warrengoldswain1108/warrengoldswain110800105/10142384-highly-detailed-fine-art-portrait-smiling-happy-real-person.jpg",
	 "114078963_amazoncom-woman-with-hand-to-face-looking-surprised-.jpg" : "http://img0062.popscreencdn.com/114078963_amazoncom-woman-with-hand-to-face-looking-surprised-.jpg",
	 "11436488-man-showing-angry-face.jpg" : "http://us.123rf.com/400wm/400/400/inspirestock/inspirestock1112/inspirestock111210311/11436488-man-showing-angry-face.jpg",
	 "12379299-young-man-expressing-disgust.jpg" : "http://static1.fjcdn.com/comments/4883144+_322d6f2722a8654ed4c559b36099bcde.jpg",
	 "1270834536-glenn-beck-crying.jpg" : "http://murylojuliani.files.wordpress.com/2010/08/1270834536-glenn-beck-crying.jpg",
	 "1276120509T8A17S.jpg" : "http://thumbs.dreamstime.com/x/cara-asustada-14663052.jpg",
	 "1281407945D03c4T.jpg" : "http://thumbs.dreamstime.com/x/confused-business-woman-15526434.jpg",
	 "1311948270220.jpg" : "http://pbs.twimg.com/media/BHriNCzCUAARWoM.jpg:large",
	 "1345666799310.jpg" : "http://pbs.twimg.com/media/BAfHmBJCMAATtvD.jpg:large",
	 "13_old.jpg" : "http://typed.kparkerdesign.net/images/13_old.jpg",
	 "1504434-979966-frederic-cirou-altopress-maxppp-woman-s-face-with-eyes-closed.jpg" : "http://www.colourbox.com/preview/1504434-979966-frederic-cirou-altopress-maxppp-woman-s-face-with-eyes-closed.jpg",
	 "156089-600x399-is-she-angry.jpg" : "http://www.menselijk-lichaam.com/wp-content/uploads/Drift-en-drijfveren.jpg",
	 "1900826-158829-face-of-surprised-young-man-with-his-mouth-open-on-black-background.jpg" : "http://www.colourbox.com/preview/1900826-158829-face-of-surprised-young-man-with-his-mouth-open-on-black-background.jpg",
	 "1AAF.jpg" : "http://greatergood.berkeley.edu/images/uploads/1AAF.jpg",
	 "20120614-DO2G5969.jpg" : "http://2.s3.envato.com/files/30533721/20120614-DO2G5969.jpg",
	 "2279322-344838-young-man-isolated-over-white-with-a-disgusted-look-on-his-face.jpg" : "http://www.colourbox.com/preview/2279322-344838-young-man-isolated-over-white-with-a-disgusted-look-on-his-face.jpg",
	 "2480546-460451-bright-picture-of-surprised-woman-face-over-white.jpg" : "http://www.colourbox.com/preview/2480546-460451-bright-picture-of-surprised-woman-face-over-white.jpg",
	 "287172f74f6eb8d572ab60b172629414.jpg" : "http://media-cache-ak0.pinimg.com/736x/28/71/72/287172f74f6eb8d572ab60b172629414.jpg",
	 "412656_4204661002767_2146606245_o.jpg" : "http://nancytanner.files.wordpress.com/2012/06/412656_4204661002767_2146606245_o.jpg",
	 "4361359-scream-of-shocked-and-scared-young-man.jpg" : "http://teenidleblog.files.wordpress.com/2013/05/grito.jpg",
	 "4980552-man-with-angry-facial-expression.jpg" : "http://us.123rf.com/400wm/400/400/maxfx/maxfx0906/maxfx090600002/4980552-man-with-angry-facial-expression.jpg",
	 "59645745_m.jpg" : "http://d3cgb598vs7bfg.cloudfront.net/images/upload-flashcards/front/5/4/59645745_m.jpg",
	 "6842757_f520.jpg" : "http://s2.hubimg.com/u/6842757_f520.jpg",
	 "72379597.jpg" : "http://pbs.twimg.com/media/BLPyrk3CMAA6pcj.jpg:large",
	 "8311_Faces05.jpg" : "http://www.tc.columbia.edu/i/media/8311_Faces05.jpg",
	 "accidental_street_portrait_01_by_54ka.jpg" : "http://blog.54ka.org/wp-content/uploads/2008/11/accidental_street_portrait_01_by_54ka.jpg",
	 "AE-GS-JCE_0132.jpg" : "http://senisimultimedia.com/wp-content/uploads/2012/01/AE-GS-JCE_0132.jpg",
	 "african-american-man-angry-expression-his-s-30569376.jpg" : "http://thumbs.dreamstime.com/z/african-american-man-angry-expression-his-s-30569376.jpg",
	 "AK-AngryCustomer.jpg" : "http://www.theoccidentalobserver.net/authors/AK-AngryCustomer.jpg",
	 "anger-how-3.jpg" : "http://static.ddmcdn.com/gif/anger-how-3.jpg",
	 "Angry-Businessman-686964.jpg" : "http://www.featurepics.com/FI/Thumb300/20080415/Angry-Businessman-686964.jpg",
	 "angry-face.jpg" : "http://www.mftrou.com/image-files/angry-face.jpg",
	 "angry-man.gif" : "http://www.aubreydaniels.com/blog/wp-content/uploads/2009/07/angry-man.gif",
	 "angry-woman.jpg" : "http://cdn.sheknows.com/articles/2010/09/angry-woman.jpg",
	 "Angry-Woman-719717.jpg" : "http://www.featurepics.com/FI/Thumb300/20080509/Angry-Woman-719717.jpg",
	 "angry3.jpg" : "http://angerasbeauty.files.wordpress.com/2010/03/angry3.jpg",
	 "angry_face_by_chrbet-d4r32mx.jpg" : "http://fc03.deviantart.net/fs71/i/2012/057/b/c/angry_face_by_chrbet-d4r32mx.jpg",
	 "Anxiety-Attack-Woman-Sad-Upset-Face.jpg" : "http://naturalnews.com/gallery/300X250/Women/Anxiety-Attack-Woman-Sad-Upset-Face.jpg",
	 "article-holmes-1221.jpg" : "http://assets.nydailynews.com/polopoly_fs/1.1225395!/img/httpImage/image.jpg_gen/derivatives/landscape_635/article-holmes-1221.jpg",
	 "bc8043570354d148902185cef6fde1da185dc875.jpg" : "http://www.memphistattler.com/BushSurprised.jpg",
	 "BLD-u10533231.jpg" : "http://www.agefotostock.com/previewimage/bajaage/94f241ad3882470af7e5c5944186fa63/BLD-u10533231.jpg",
	 "blond_woman_with_surprised_face_close_up_020DPI00234.jpg" : "http://www.visualphotos.com/photo/1x6885659/blond_woman_with_surprised_face_close_up_020DPI00234.jpg",
	 "BodyLanguageProjectCom-Primary-Emotions-Disgust.jpg" : "http://bodylanguageproject.com/the-only-book-on-body-language-that-everybody-needs-to-read/wp-content/uploads/2013/03/BodyLanguageProjectCom-Primary-Emotions-Disgust.jpg",
	 "brain9-11.jpg" : "http://www.sott.net/image/image/1138/brain9-11.jpg",
	 "Businesswoman-Accusing-688149.jpg" : "http://www.featurepics.com/FI/Thumb300/20080415/Businesswoman-Accusing-688149.jpg",
	 "c2.jpg" : "http://www.microexpressionstrainingvideos.com/wp-content/uploads/2012/11/c2.jpg",
	 "chris-brown-sad-face.jpeg" : "http://s3.amazonaws.com/rapgenius/chris-brown-sad-face.jpeg",
	 "confused-face.jpg" : "http://s3.amazonaws.com/rapgenius/1362353064_confused-face1.jpg",
	 "Confused-face-e1268404997164-266x300.jpg" : "http://static2.fjcdn.com/comments/mfw+the+tags+_420bae8478648638446e5fb1e803978b.jpg",
	 "Confused_Woman_op_576x335.jpg" : "http://3dwave.net/wp-content/uploads/2013/05/Confused_Woman_op_576x335.jpg",
	 "Cynthia-Khater-Disgust.jpg" : "http://bassbrass.org/Images/Facial%20Expressions/Cynthia-Khater-Disgust.jpg",
	 "dawson-crying.jpeg" : "http://pbs.twimg.com/media/A_pMO8qCEAEdz8l.jpg:large",
	 "depositphotos_8940587-Businessman-detects-bad-odor.jpg" : "http://static8.depositphotos.com/1005357/894/i/950/depositphotos_8940587-Businessman-detects-bad-odor.jpg",
	 "depositphotos_9811730-Beautiful-young-happy-woman-holding-hands-to-face-in-surprise.jpg" : "http://static8.depositphotos.com/1023162/981/i/950/depositphotos_9811730-Beautiful-young-happy-woman-holding-hands-to-face-in-surprise.jpg",
	 "disappointed-disgusted-young-man-handsome-expression-isolated-white-background-30894174.jpg" : "http://thumbs.dreamstime.com/z/disappointed-disgusted-young-man-handsome-expression-isolated-white-background-30894174.jpg",
	 "disgust-2.jpg" : "http://facialexpressionsproject.files.wordpress.com/2011/03/disgust-2.jpg",
	 "Disgust-face.jpg" : "http://img.4plebs.org/boards/tg/image/1368/06/1368061235923.jpg",
	 "Disgust-Sensitivity-Extends-to-Visual-Perception-SS.jpg" : "http://g.psychcentral.com/news/u/2012/12/Disgust-Sensitivity-Extends-to-Visual-Perception-SS.jpg",
	 "disgusted.jpg" : "http://i.livescience.com/images/i/000/048/264/original/disgusted-101130-02.jpg",
	 "disgusted2.jpg" : "http://www.buzzle.com/images/people/body-language/disgusted.jpg",
	 "dr who scared face.jpg" : "http://ready-for-ten.s3.amazonaws.com/posts/assets/22382/large/dr%20who%20scared%20%20face.jpg",
	 "DSC02542.jpg" : "http://sweettoothrunner.com/wp-content/uploads/2011/08/DSC02542.jpg",
	 "ee8edb1d-e95a-42a8-81cd-caa897a45da4.jpg" : "http://thumbs.imagekind.com/4049191_650/This-is-my-surprised-face.jpg",
	 "ekman_disgust.jpg" : "http://www.neurodiversity.com/nvc/ekman_disgust.jpg",
	 "eyes-closed-hand-to-face.jpg" : "http://blog.pharmacymix.com/wp-content/uploads/2012/04/eyes-closed-hand-to-face.jpg",
	 "Fear.jpg" : "http://www.social-engineer.org/resources/newsletters/isu10/Fear.JPG",
	 "face-eyes-closed-57.4.jpg" : "http://philip.greenspun.com/images/pcd2668/face-eyes-closed-57.4.jpg",
	 "fearii6.jpg" : "https://lh4.googleusercontent.com/-BxLBNpiM_Lg/TjCzcxhI6fI/AAAAAAAAbTw/_CaHm2zqLXU/s800/fearii6.jpg",
	 "fotd-clinique-happy-bright-110307-closeup.jpg" : "http://www.makeupandbeautyblog.com/wp-content/uploads/2007/11/fotd-clinique-happy-bright-110307-closeup.jpg",
	 "Frightened-1314803.jpg" : "http://www.featurepics.com/FI/Thumb300/20090906/Frightened-1314803.jpg",
	 "frightened-facial-expression-4_medium.jpg" : "http://etc.usf.edu/clippix/pix/frightened-facial-expression-4_medium.jpg",
	 "Funny Angry Face_1.jpg" : "http://1.bp.blogspot.com/-pZCck9PJA-A/UHwC1yMkJMI/AAAAAAAAAqc/NcnLtu1Rmyo/s1600/Funny%2BAngry%2BFace_1.jpg",
	 "Funny-Scared-Faces-03.jpg" : "http://www.funnydayz.com/wp-content/uploads/2012/09/Funny-Scared-Faces-03.jpg",
	 "Greg-Angry-Face.jpg" : "http://darkmarkets.com/wp-content/uploads/2010/03/Greg-Angry-Face.jpg",
	 "happy-man32.jpg" : "http://www.rigabrain.com/blog/wp-content/uploads/2013/09/Klientu-atsauksmes.jpg",
	 "health-benefits-of-smiling-07-pg-full.jpg" : "https://lh3.googleusercontent.com/-rvXG99bVBm0/UsXBGGbx3lI/AAAAAAAAAUQ/zzFIePwm1OU/s426/cd400ed1-cb55-41f8-85ec-9ca3b827f813",
	 "HisF070034A.jpg" : "http://www.humintell.com/wp-content/uploads/2010/08/HisF070034A.jpg",
	 "IMG_1990.jpg" : "http://www.humintell.com/wp-content/uploads/2010/08/IMG_1990.jpg",
	 "iStockphoto_angry_0.jpg" : "http://cdn2-b.examiner.com/sites/default/files/styles/image_content_width/hash/fd/ba/iStockphoto_angry_0.jpg",
	 "javi-martinez-angry-face-close-up-profile-footballer-model-promo-product-shill-79896181.jpg" : "http://us.cdn291.fansshare.com/photos/javimartinez/javi-martinez-angry-face-close-up-profile-footballer-model-promo-product-shill-79896181.jpg",
	 "k-bigpic.jpg" : "http://img.gawkerassets.com/img/18j2ovdj5jvpzjpg/k-bigpic.jpg",
	 "m1110196-rachel-fear-261x300.jpg" : "http://www.facscodinggroup.com/wp-content/uploads/2011/01/m1110196-rachel-fear-261x300.jpg",
	 "man-angry-face-107996.jpg" : "http://thumbs.dreamstime.com/z/man-angry-face-107996.jpg",
	 "Man_Scared_Face_Reference_by_ahtibat_stock1.jpg" : "http://iampierremenard.files.wordpress.com/2012/07/man_scared_face_reference_by_ahtibat_stock.jpg",
	 "Me-Scared-as-Shit.jpg" : "http://ricoswaff.com/blog1/wp-content/uploads/2013/04/Me-Scared-as-Shit.jpg",
	 "men-expressing-disgust-16362250.jpg" : "http://thumbs.dreamstime.com/x/men-expressing-disgust-16362250.jpg",
	 "martin-pouts-too.jpg" : "http://thepitwalk.files.wordpress.com/2010/10/martin-pouts-too.jpg",
	 "mmw-digust-religion.jpg" : "http://www.psmag.com/wp-content/uploads/2011/05/mmw-digust-religion.jpg",
	 "Navarasam-Bhibatsam-Disgust.jpg" : "http://www.kathakalischool.com/images/Navarasam-Bhibatsam-Disgust.jpg",
	 "Niall-Horan-TaylorSwift1-copy.jpg" : "http://buzzworthy.mtv.com//wp-content/uploads/buzz/2013/06/Niall-Horan-TaylorSwift1-copy.jpg",
	 "Nikia-Close-Up-of-Face-with-Eyes-Closed.jpg" : "http://cdn.c.photoshelter.com/img-get2/I0000RS5YBzZC.d4/fit=1000x870/Nikia-Close-Up-of-Face-with-Eyes-Closed.jpg",
	 "o.jpg" : "http://www.pocketsalute.it/new/wp-content/uploads/2013/09/guiducci.jpg",
	 "oh-face.jpg" : "http://flashinthepanreviews.files.wordpress.com/2011/05/oh-face.jpg",
	 "oprah-surprised-face_thumb.jpg" : "http://manonthelam.com/wp-content/uploads/2011/12/OPRAH-surprised-face_thumb.jpg",
	 "PaulRyanSad.jpg" : "http://p.twimg.com/A0LhcNFCEAAuHK8.jpg:large",
	 "qtjxtd67-1335919981.jpg" : "https://c479107.ssl.cf2.rackcdn.com/files/10223/wide_article/width926x450/qtjxtd67-1335919981.jpg",
	 "rach.jpg" : "http://blog.biznik.com/images/blog_art/rach.jpg",
	 "recoverydivorce-300x268.jpg" : "http://www.coach-amoureux.com/wp-content/uploads/2012/12/Reconqu%C3%A9rir-Son-Homme-300x268.jpg",
	 "resize_1380121048_uploads_images_0257a624bdb15fff00a9d9d9f91f9c29_jpg_610x0_85.jpg" : "http://www.dental-tribune.com/thumbCache/8/4/0/resize_1380121048_uploads_images_0257a624bdb15fff00a9d9d9f91f9c29_jpg_610x0_85.jpg",
	 "sadmom.jpg" : "http://diglib.eg.org/EG/DL/conf/EG2011/posters/MM/015-016/010.jpg",
	 "SamsScaredFace.jpg" : "http://static2.fjcdn.com/comments/YFW+the+thief+uses+it+against+you+_7a7eb1003a940b6facb73e44402f00c6.jpg",
	 "scared-face-002.jpg" : "http://1.bp.blogspot.com/-q4cVuLYiiiY/TlIuMls2HnI/AAAAAAAAB30/GHc5Mvyf_YI/s1600/darna.jpg",
	 "scared-face.jpg" : "http://sarahsomewhere.com/wp-content/uploads/2012/09/scared-face.jpg",
	 "scared_man.jpg" : "http://3.bp.blogspot.com/_Fc3MQ-NoGw4/TRmHbQILe3I/AAAAAAAAGYk/yJcHy15LnsE/s1600/scared_man.jpg",
	 "sexy_angry_face_by_tsene-d50yrp6.jpg" : "http://fc01.deviantart.net/fs70/f/2012/144/3/d/sexy_angry_face_by_tsene-d50yrp6.jpg",
	 "smile-it-could-make-you-happier_1.jpg" : "http://www.scientificamerican.com/media/inline/smile-it-could-make-you-happier_1.jpg",
	 "superstock_255-11889.jpg" : "http://wwwdelivery.superstock.com/WI/223/255/PreviewComp/SuperStock_255-11889.jpg",
	 "SuperStock_1569R-9019411.jpg" : "http://wwwdelivery.superstock.com/WI/223/1569/PreviewComp/SuperStock_1569R-9019411.jpg",
	 "surprised_man.jpg" : "http://4.bp.blogspot.com/-8XjwZ2hO9Q8/TumRtrSAmUI/AAAAAAAAAts/TJt-uHluWSM/s1600/surprised.jpg",
	 "Surprised-face.jpg" : "http://s3.amazonaws.com/rapgenius/1bnrrPdsSYib7Dt0eIsa_surprised_face.jpg",
	 "surprised.jpg" : "http://danielakawmd.files.wordpress.com/2010/03/surprised.jpg",
	 "surprised-face (1).jpg" : "http://i.imgur.com/ZZbKXug.jpg",
	 "surprised_face_mugshot.jpg" : "http://iamnotashamedofthegospelofchrist.files.wordpress.com/2013/06/surprised_face_mugshot.jpg",
	 "surprised_mans_face_post_card-r4fbe082d1fc14b399d89e2054e72c692_vgbaq_8byvr_324.jpg" : "http://rlv.zcache.com/surprised_mans_face_post_card-r4fbe082d1fc14b399d89e2054e72c692_vgbaq_8byvr_324.jpg",
	 "surprised-woman-in-red.jpg" : "http://southeastidahooralsurgery.com/wp-content/uploads/2012/10/surprised-woman-in-red.jpg",
	 "cristiano-ronaldo-517-bad-humor-and-angry-face-in-portugal-at-euro-2012.jpg" : "http://techjost.com/wp-content/uploads/2012/06/cristiano-ronaldo-517-bad-humor-and-angry-face-in-portugal-at-euro-2012.jpg",
	 "ti1603137.jpg" : "http://comp.webstockpro.com/tetraimages/ti1603137.jpg",
	 "tommy_disgusted_face_by_seanvollfied-d4agb6w.jpg" : "http://fc01.deviantart.net/fs71/i/2011/263/d/0/tommy_disgusted_face_by_seanvollfied-d4agb6w.jpg",
	 "tumblr_mavy5nXNu61qg6hyi.jpg" : "http://static4.fjcdn.com/comments/+_a1a93abd73223d5fde3c2a5c30c18f25.jpg",
	 "young-male-doctor-very-surprised-face-10630920.jpg" : "http://thumbs.dreamstime.com/z/young-male-doctor-very-surprised-face-10630920.jpg",
	 "Wentworth Miller Looking At Camera Angry Face Photoshoot.jpg" : "http://downloads.xdesktopwallpapers.com/wp-content/uploads/2012/04/Wentworth%20Miller%20Looking%20At%20Camera%20Angry%20Face%20Photoshoot.jpg",
	 "what-will-future-historians-think-about-us-1430690829-nov-12-2012-1-600x500.jpg" : "http://web-images.chacha.com/images/Gallery/5075/what-will-future-historians-think-about-us-1430690829-nov-12-2012-1-600x500.jpg",
	 "will-smith-is-confused.jpg" : "http://wordsmithjournal.files.wordpress.com/2013/07/will-smith-is-confused.jpg",
	 "wmphoto-24769183-man-gesturing-an-angry-face.jpg" : "http://cdn4.qualitystockphotos.com/b1/12/123/photo-24769183-man-gesturing-an-angry-face.jpg",
	 "woman_making_surprised_face_137BER00440.jpg" : "http://www.visualphotos.com/photo/1x6923451/woman_making_surprised_face_137BER00440.jpg",
	 "woman_with_angry_face_020DPI00224.jpg" : "http://www.visualphotos.com/photo/1x6885651/woman_with_angry_face_020DPI00224.jpg",
	 "woman-with-angry-expression.jpg" : "http://images.parexcellencemagazine.com/stories/wisdom_and_wellbeing_articles/woman-with-angry-expression.jpg",
	 "Zooey-Deschanel O-Face.jpg" : "http://www.seyvet.com/resim/9249ecfa2f.jpg",
	 #flickr
	 "104810657_1ce2931c9f.jpg" : "http://farm1.staticflickr.com/36/104810657_1ce2931c9f.jpg",
	 "133232468_ff40c155af_o.jpg" : "http://farm1.staticflickr.com/45/133232468_ff40c155af_o.jpg",
	 "168378170_e66240f1f3_b.jpg" : "http://farm1.staticflickr.com/70/168378170_e66240f1f3_b.jpg",
	 "1824233430_7813aa31fa_b.jpg" : "http://farm3.staticflickr.com/2049/1824233430_7813aa31fa_b.jpg",
	 "212002_d5613ee416_z.jpg" : "http://farm1.staticflickr.com/1/212002_d5613ee416_z.jpg",
	 "1676198388_30e4eb62ea_z.jpg" : "http://farm3.staticflickr.com/2375/1676198388_30e4eb62ea_z.jpg?zz=1",
	 "2256470202_de1044716f_b.jpg" : "http://farm3.staticflickr.com/2285/2256470202_de1044716f_b.jpg",
	 "2281682873_947091f2c1_o.jpg" : "http://farm3.staticflickr.com/2304/2281682873_947091f2c1_o.jpg",
	 "2282473450_36743d92f3_o.jpg" : "http://farm4.staticflickr.com/3113/2282473450_36743d92f3_o.jpg",
	 "2346203472_6e561ba2f3_b.jpg" : "http://farm3.staticflickr.com/2257/2346203472_6e561ba2f3_b.jpg",
	 "247592149_13d8479bc3_o.jpg" : "http://farm1.staticflickr.com/94/247592149_13d8479bc3_o.jpg",
	 "2586499735_61b7448aaf_z.jpg" : "http://farm4.staticflickr.com/3030/2586499735_61b7448aaf_z.jpg",
	 "2639866611_c3ecd37bce_b.jpg" : "http://farm4.staticflickr.com/3281/2639866611_c3ecd37bce_b.jpg",
	 "2689807493_d738299372_o.jpg" : "http://farm4.staticflickr.com/3235/2689807493_d738299372_o.jpg",
	 "2721823832_34f9b4d14d_b.jpg" : "http://farm4.staticflickr.com/3223/2721823832_34f9b4d14d_b.jpg",
	 "2938447779_8603bd4638_z.jpg" : "http://farm4.staticflickr.com/3149/2938447779_8603bd4638_z.jpg?zz=1",
	 "3040230908_11a8f06294_b.jpg" : "http://farm4.staticflickr.com/3201/3040230908_11a8f06294_b.jpg",
	 "3206773159_b6f86c1a3e_b.jpg" : "http://farm4.staticflickr.com/3342/3206773159_b6f86c1a3e_b.jpg",
	 "3259673718_d31562e257_b.jpg" : "http://farm4.staticflickr.com/3519/3259673718_d31562e257_b.jpg",
	 "3334719929_17655be093_b.jpg" : "http://farm4.staticflickr.com/3608/3334719929_17655be093_b.jpg",
	 "3358153294_2a757b2db3_b.jpg" : "http://farm4.staticflickr.com/3615/3358153294_2a757b2db3_b.jpg",
	 "340040742_e6b84beb34_o.jpg" : "http://farm1.staticflickr.com/161/340040742_e6b84beb34_o.jpg",
	 "3460075040_02a0472fa1_b.jpg" : "http://farm4.staticflickr.com/3647/3460075040_02a0472fa1_b.jpg",
	 "3812488835_7206242b54_z.jpg" : "http://farm3.staticflickr.com/2485/3812488835_7206242b54_z.jpg?zz=1",
	 "3918719435_977f32eca5_b.jpg" : "http://farm3.staticflickr.com/2520/3918719435_977f32eca5_b.jpg",
	 "4026010483_99f7ebae3b_b.jpg" : "http://farm3.staticflickr.com/2618/4026010483_99f7ebae3b_b.jpg",
	 "4191715398_1569888c69_z.jpg" : "http://farm3.staticflickr.com/2579/4191715398_1569888c69_z.jpg",
	 "424661994_180a98e904_b.jpg" : "http://farm1.staticflickr.com/186/424661994_180a98e904_b.jpg",
	 "4248753142_ea51eea117.jpg" : "http://farm3.staticflickr.com/2723/4248753142_ea51eea117.jpg",
	 "4252205498_342f92713e_b.jpg" : "http://farm5.staticflickr.com/4003/4252205498_342f92713e_b.jpg",
	 "4341276374_636d04c3d8_b.jpg" : "http://farm5.staticflickr.com/4015/4341276374_636d04c3d8_b.jpg",
	 "4427515943_9b72d247a0_z.jpg" : "http://farm3.staticflickr.com/2784/4427515943_9b72d247a0_z.jpg?zz=1",
	 "465311994_9d96bad375_z.jpg" : "http://farm1.staticflickr.com/196/465311994_9d96bad375_z.jpg",
	 "4746638615_9f6c51eac0_z.jpg" : "http://farm5.staticflickr.com/4143/4746638615_9f6c51eac0_z.jpg",
	 "5266866878_af48ac280e_b.jpg" : "http://farm6.staticflickr.com/5049/5266866878_af48ac280e_b.jpg",
	 "5345121635_b54b9f08e6_b.jpg" : "http://farm6.staticflickr.com/5003/5345121635_b54b9f08e6_b.jpg",
	 "5600487733_2f6fe05e90.jpg" : "http://farm6.staticflickr.com/5106/5600487733_2f6fe05e90.jpg",
	 "5962923003_c5eca00a1c_b.jpg" : "http://farm7.staticflickr.com/6029/5962923003_c5eca00a1c_b.jpg",
	 "5771938154_8ec3c029f7_z.jpg" : "http://farm4.staticflickr.com/3224/5771938154_8ec3c029f7_z.jpg",
	 "5825834776_163ed4881c_b.jpg" : "http://farm6.staticflickr.com/5061/5825834776_163ed4881c_b.jpg",
	 "5885703466_a2474526b3_b.jpg" : "http://farm6.staticflickr.com/5271/5885703466_a2474526b3_b.jpg",
	 "5914349990_89489be02e_b.jpg" : "http://farm7.staticflickr.com/6039/5914349990_89489be02e_b.jpg",
	 "5914664940_21e0c173f4_b.jpg" : "http://farm6.staticflickr.com/5312/5914664940_21e0c173f4_b.jpg",
	 "624460616_4edd278c94_b.jpg" : "http://farm2.staticflickr.com/1355/624460616_4edd278c94_b.jpg",
	 "6845138387_371b34c23e_b.jpg" : "http://farm8.staticflickr.com/7014/6845138387_371b34c23e_b.jpg",
	 "694519309_817d37fd1d_b.jpg" : "http://farm2.staticflickr.com/1325/694519309_817d37fd1d_b.jpg",
	 "7982522108_8105c14a96.jpg" : "http://farm9.staticflickr.com/8458/7982522108_8105c14a96.jpg",
	 "863846941_4f2d5a4009_z.jpg" : "http://farm2.staticflickr.com/1368/863846941_4f2d5a4009_z.jpg?zz=1",
}

for fi, url in files.iteritems():
  if not os.path.exists(os.path.join("./images",fi)):
    # download
    try:
      r = requests.get(url, stream=True)
      if 'Content-Length' in r.headers:
        size = int(r.headers['Content-Length'].strip())
        bytes = 0
        f = open(os.path.join("./",fi), 'wb')
        print "Downloading: %s Bytes: %s" % (fi, size)
        for buf in r.iter_content(1024):
          if buf:
            f.write(buf)
            bytes += len(buf)
            status = r"%10d	 [%3.2f%%]" % (bytes, bytes * 100. / size)
            status = status + chr(8)*(len(status)+1)
            print status,
      else:
        bytes = 0
        f = open(os.path.join("./",fi), 'wb')
        print "Downloading: %s" % (fi)
        for buf in r.iter_content(1024):
          if buf:
            f.write(buf)
            bytes += len(buf)
            status = r"%10d	 " % (bytes)
            status = status + chr(8)*(len(status)+1)
            print status,
      f.close()

      # move to correct directory
      shutil.move(os.path.join("./",fi), "./images")
    #except KeyError:
    #  import pdb;pdb.set_trace()
    except:
      print "Could not find image at the url: %s" % (url)
	
print "Done!"