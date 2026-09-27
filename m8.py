#!/usr/bin/env python3
"""
m8.py — Free Fire OB55 standalone matchmaking bot.

Self-contained. No external files. Only dependencies:
    pip install requests pycryptodome

Usage:
    python3 m8.py --uid 4418453178 --password "PW" --region IND --duration 300
"""

import time, json, socket, secrets, hashlib, hmac, argparse, sys, threading, base64, re, os
import requests, urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================================
# EMBEDDED STATIC DATA
# =====================================================================
INIT_1_HEX = '080212d2030acf036db490ebec9ac7b07b01d5762b2a1595c4d52a248fa3cc0fda3d55efe75231ce2cd785d46460f116bfb9711bb54de42e20039b4d42c6e17fc3a24ab860dc9d445fef68ff9a6d39dbaab068f75c9f00383e2131fea1dc0a08d15c7a8eebc22aaf11feacf050fa1d185c24d12ae227d84da6ed47c186c835a4411e7b287a468b44e7efd6b38d6ff36e16af16e7d45e61366363fa9e6693d98f35561fed90b3d3c588aab860ec759a25847bbba267d5709515cdb2044ff6519dd825bf6a29aaee481e13b948a8c0bae9e1aff0bdafb2f1ff77b49d758156c0abd2bb7be5d70b9be5bba33387b861b64882fbad474a3bc7f0a4d992105ef2db852bfbada92916a506f4a5fa9d085bf03c16085d6afd336b1fc17edba6660aa319f79287f10f46d47998fb11b5e35840ac114c8c952c4ffc38983f658aceae5f2cd96dfb27016d94923cee65bc3750d568dd6b83e3d7865815d5d3c1a43d109d53ce19706f91e41bbb2a94ab1cfc12dfcdd160bd48b95a48b81f43c562d9f5050556e881d7d216d338bd0d4be9f48da68da97e5d4d8ada71c4629ae6d52534b388e56d5846c9d73c42facb0630c4418aff99c56db03abba8a4f36369dca207c5eeb9a6a61755ff7a909ca2b6e8580a480b1078fb6bb1ac2e'

INIT_2_HEX = '080b12f5060af2063c7046e580af3f0ef9292ec8e9620f105448dc67d6e9f531d3e4680538d19808d38b16c831bebbe6cbf26caf2c67d0cb6cc7b8dcb228ee86cb4044f0a3202bc5f358b69fe7ab7352796de6c37a6bdcc57c794b453d0fb2bd1daec383f73779bda099aa4ea7b327cfe450fb14583857959a78e139f6bfcfefa7b357848ada59b8f8cb98be6a49fec7784ccf2fe7a7ee803f1f3c76ad42195f8a2157aff9ce6ec4d5c95efa5ec75d61b721605ec4e0c72c227d3daed285bcbfdb31f0cb8ec3f5524e290e3d706e9dcb4ddbf6ff2783e4b33531e8b0c7a930ddb295a486d82e4be91a9070b1fb1c0c0257c57584b625fdec767d5e9d921f69c70870519d0f23d7b0eddb51dc971aeeca7d501229778e4a93441a2ed10c67775bdd2a78d971543ba6d57a43eab8d37ae9c0f23ffd6c82a4eac55467ad6af63b0d9461b8bb1e3a7e77e008df11a1b85175b409fbc8026673311bc323a047eb6b2db1e3a6f338d3db466172422dfd4d8030fa4be2fb40c0f0e211dee71809438b6fcb66fd7b35bdfd55e22feadb999eff3a686f7514cf95fa55064419fed83d2e10814037d37f94fd0012797c20f468d4d77f14f66721a1ceb24aaca95d717c0b4569a84a7ba4331603fdba0816119d5754a571630cb90543c314533985c427d2f913c2d8f6ee641326fe38a35abe67e4125f59a308d58aac7a7368c824be14c514b0caa7acae3e38f3093d49bf795126288eb3bd1425aa6e27e033a0cec8fbb92155b8577479d00c0d749b4ed75f5f71677f7682a8751cf974d2b9233d6962f13d02a5d1d64fb842742a452f9e9ef80dc5a65959c18150c0d56b98bad3b25ecfbdf4cf37e63bcd78714aea6371ef857f6b641c5f7404aca7dd93b58819038d989c24d710974d5e9c924bcfbfd95934e6153fd540093b98690d0a855d691daa8e0bd1f4088044233cf281574cf2a714b32e0b8d083d63286f5c33e15f679325686e78ffc8060397c9a40009eed239690cc7b458400a47c4a7017400262059d34eabbae2bb6fb7356d3bb8a044b4a8592e5ee37f967843156474708679e140fd9bb86252a16f1738215a48c528dbf745b84e928aab7df47c64910b6e6e1350a684ef988295c98ef9e8d9aa3eecfa0435dbcd97d52c0cf207b4c6defc5e83d07284570ac6dfc1dc1881118c20fd7bd21e4860bfb2651fbd35050422906ccc8901ddae0ad4167251203b096edde3def0ab0b7f72f4ae83cabfa1450a4f'

CONFIRM_HEX = '080712d8031202656e1acf036db490ebad627edc7b01d5762b2a1595c4d52a248fa3cc0fda3d55efe75231ce2cd785d46460f116bfb9711bb54de42e20039b4d42c6e17fc3a24ab860dc9d445fef68ff9a6d39dbaab068f75c9f00383e2131fea1dc0a08d15c7a8eebc22aaf11feacf050fa1d185c24d12ae227d84da6ed47c186c835a4411e7b287a468b44e7efd6b38d6ff36e16af16e7d45e61366363fa9e6693d98f35561fed90b3d3c588aab860ec759a25847bbba267d5709515cdb2044ff6519dd825bf6a29aaee481e13b948a8c0bae9e1aff0bdafb2f1ff77b49d758156c0abd2bb7be5d70b9be5bba33387b861b64882fbad474a3bc7f0a4d992105ef2db852bfbada92916a506f4a5fa9d085bf03c16085d6afd336b1fc17edba6660aa319f79287f10f46d47998fb11b5e35840ac114c8c952c4ffc38983f658aceae5f2cd96dfb27016d94923cee65bc3750d568dd6b83e3d7865815d5d3c1a43d109d53ce19706f91e41bbb2a94ab1cfc12dfcdd160bd48b95a48b81f43c562d9f5050556e881d7d216d33dbd0d4be9f48da68da97e5d4d8ada71c4629ae6d52534b388e56d5846c9d73c42facb0630c4418aff99c56db03abba8a4f36369dca207c5eeb9a6a61755ff7a909ca2b6e8580a480b1078fb6bb1ac2e2801'

TICKETS_HEX = [
    '080112ac0a0a0301161d100f3a0d0a044944433110b8171a024e4140064a0f01030407090a0b1216191a201d2729580162c7090a403238303230303034343135413146374230323031303030303030303030303030303030303030303030303030303030303944444131384542303030303030303010481ab9037e585a531704034f05005408550f0e520401030f0e060d060204575101075003575a0706575500061007064e7d5c46424d1d031f071e1109034a06527b7100596f43627e7c644d437165587e760e770e637f077a7e0b1403447b5b645573507e4c78667f76505770734a5878565d5a5b575767420e1050585c4c1e657e19724343044b6a55777e615e64456b5f675e50500657525d045a7902037005007f091602004a40704d574659775167040f047a75427c59457a7d0b057942517a410b170d4f4701671d536264196e0c77406c5d4153437f5d4d1e7d18594f41790c1504481e754b5271431740575e7b5b694141445f5a03060f604d03415f7e0f1b084a676d747f1c43636317505b6f7f4f4a7d737d195269037e474706070b1403004d730f79015c4a527961546544724d4d697e01437f0c706f077977580e15044e701a075267660277401c005e055e600154461859047513771d61040810074a514b7f50417c6d7402626f0240696870036741501c454d057f74730b1707034f47700413505f447a527f415d62664a434307034d7d00435e7d4f700b1501495c45455e7a5e5f5d774657465e1d63755041557c65421c0a626d4505220478585c5d300c3a08107d79667d73161c4207312e3133322e37480350025aa5050362625351362f6c7574485176416456324b796f566c53566b78624b447a676d6b5134727532325434774467586c364d5241505373315a35355a4742634d3636714a523563755635595a6d4663767134514449504939704c39644442536a68355857687a44702f47545a5031724d4c595057474d736458767452583168574131737863636f733077737737363664557078436b4a5a62645279637135744f4a57594448416d6730325267494164654a6d2b4d42785661784170564a4f6a705a6633695458696479634b4355523536447143653249306b64774b50347453727157674171365138774b48514942685231795451705a4f6c6c7059496e2f4e4376487072343052676d4845676d596a6433637444735a546e434935327a5a4d614a4e326570466365516e543441624a4d5842554f2f5373756c446c6b68784c4b6975414945594d4a79795a4f5368443341746d6f5a4b6e6e536339464b385856426d562f446b3644413644644f41653656566664734345356a4a35453873335958636d377a6a722b6b613937366f50666b6d575a70565a2f2f49436665346442654a556349777a6f546c5a754b4f6f6c366b57764e325770334f62375632316b414e546870636a656231416c6c6e492b2b636d464b4f454d42657868374c36692b45534e434d764f4e37416530774e35742f72522b37556f5052302f7762664f765a6872736656344c733062624674674f51636f2f657872763255574b487558417350506855327a723254396e47393839542b663346577a6b4831463457386d47426f57377a3733757a6e516b337543575479594f70374d6453445271445768536a79795065524833586575384a442b6676617a4946765174455150694b7a506d397275315a6159477177572f614e69583654456f68382b58734f55326f4c613346715a765445880129a201050803108a03a201050804108703a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815',
    '080112a80a0a02011d100f3a0d0a044944433110b8171a024e4140014a0f01030407090a0b1216191a201d2729580162c7090a403238303230303034343135413146374230323031303030303030303030303030303030303030303030303030303030303944444131384542303030303030303010591ab9037e585a531704034f05005408550f0e520401030f0e060d060204575101075003575a0706575500061007064e7d5c46424d1d031f071e1109034a06527b7100596f43627e7c644d437165587e760e770e637f077a7e0b1403447b5b645573507e4c78667f76505770734a5878565d5a5b575767420e1050585c4c1e657e19724343044b6a55777e615e64456b5f675e50500657525d045a7902037005007f091602004a40704d574659775167040f047a75427c59457a7d0b057942517a410b170d4f4701671d536264196e0c77406c5d4153437f5d4d1e7d18594f41790c1504481e754b5271431740575e7b5b694141445f5a03060f604d03415f7e0f1b084a676d747f1c43636317505b6f7f4f4a7d737d195269037e474706070b1403004d730f79015c4a527961546544724d4d697e01437f0c706f077977580e15044e701a075267660277401c005e055e600154461859047513771d61040810074a514b7f50417c6d7402626f0240696870036741501c454d057f74730b1707034f47700413505f447a527f415d62664a434307034d7d00435e7d4f700b1501495c45455e7a5e5f5d774657465e1d63755041557c65421c0a626d4505220478585c5d300c3a08107d79667d73161c4207312e3133322e37480350025aa50503626253513633685335585976416456324b796f566c53566b78624b447a6e613051347075656553556d41476c714f494b545552714d344b4874746f6e6d31727949683545794778553541494c4f6673386e69654f32656c66317565697943386754357751556b6d594f414b64516d732f71434556756b48652f2b7a7761447a795373744a44757374383548574e375642616649653643574c5a497247732f7a71586e6f4761715645622b6c464850745677384a79487a476530333655564f73473544627a4f34446f64766a366d513667716352704d4434335a396242496c4b6959344d436c2f4336457a416872796d37497466442b596d73666f4d4970336d654b393639722f7158326e68744c6776794f63394532523369766c5749786e396a4f4b764a4f626d6c6f4d4e64725354614338486d674d6c61377736464f71724774386538484e544744427979726b6d702b572f4566526f4435673163342b2f6956464c62574274776763573345447563355668724635476354766f57396f654e7875745947567536572f6264354274466a424469436c6959626b6e596a72304277557972434f6d5573306b466a79772f7339724336612b324e734b38544c522f507050724e48414e52682b33487549644c6668526a43735576464c58556d452f65646756434d642f4f7374735a6f4e4156316564687744487a306469436f3668504e356576756b5a78384f7849624258466a70656f6f5574373977524a4f427248367737646f3975415473437a6d3070704b436b4b4e49386d394c6a42574d6f357946597a633055796f5675505331362b59324f727048724f774e4d447a63383048722b717363576f534e465441697955396a344e364b4151557069554a4468453132717145306e54656a6e72357237546c716141565736784c2f6c4c4141344146754ca201050803108a03a201050804108703a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815',
    '080112a50a0a0301161d100f3a0d0a044944433110b8171a024e4140064a0f01030407090a0b1216191a201d2729580162c0090a403238303230303034343135413146374230323032303030303030303030303030303030303030303030303030303030304533344631384542303030303030303010b1011ab9037e585a531704034f05005408550f0e520401030f0e060d060204575101075003575a0706575500061007064e7d5c46424d1d031f071e1109034a06527b7100596f43627e7c644d437165587e760e770e637f077a7e0b1403447b5b645573507e4c78667f76505770734a5878565d5a5b575767420e1050585c4c1e657e19724343044b6a55777e615e64456b5f675e50500657525d045a7902037005007f091602004a40704d574659775167040f047a75427c59457a7d0b057942517a410b170d4f4701671d536264196e0c77406c5d4153437f5d4d1e7d18594f41790c1504481e754b5271431740575e7b5b694141445f5a03060f604d03415f7e0f1b084a676d747f1c43636317505b6f7f4f4a7d737d195269037e474706070b1403004d730f79015c4a527961546544724d4d697e01437f0c706f077977580e15044e701a075267660277401c005e055e600154461859047513771d61040810074a514b7f50417c6d7402626f0240696870036741501c454d057f74730b1707034f47700413505f447a527f415d62664a434307034d7d00435e7d4f700b1501495c45455e7a5e5f5d774657465e1d63755041557c65421c0a626d4505220478585c5d300c3a08107d79667d73161c4207312e3133322e37480350025a9d050362625351362f4f5573397368416456324b796f566c5163442b786f50785363485459396363557448624a6c566c504356746d544a422f736250676e57694a456f4746326e35645633546866736c4c68554d3969536f6943757443494f4451772f613738396e5159432b62652f336641466f635071346d4f7a4333576d68467251684a78664c37574b767a546a7478737042634653424261636544766433374b695231706673305132436e57785070494c5247714648724a414b6d6e50334d2f55392f357a54547374483138743062697233614e694961695265503779566e674d5536743631466668637333335645495173595064302b495649476a4575636e6f5569616c713876346b793858317574496a65722f557141665343734a464d664b7079462b78426f4d2f376f6e52417147526759536e343969766d4633746b646c6e7a6a6f31736845615351616f64556c796246416f78786756747463346c75536735686431657057497746512b7342312b65536c4e456a4769504e466656714b594a3330766e31466455743031702f6a5a314d44695949454d6377414e3061543177614a39446a683658587a76537474464278555035736b483532327a6b69566a482f753242327778394b557367314f3848754136704558547737426d5a464c595a69674f6754346a4b756f72436948476a47684842573178586f7146347742344d763457454f506f3141665a712b4356595663674c4733746d775645366d496e41706834476843714e38396b49506f563547683868465965694b7475503646644a763449794d2f326950396e69543534624d636e6e41454745763057504b696967735469494a6e766a326b55392b777a69686b497a7675624a4a36387451616e356266614167507a48647270584c31784364324c47466b6f526d49880129a201050803108a03a201050804108703a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815',
    '080112b10a0a0301161d100f3a0d0a044944433110b8171a024e4140064a0f01030407090a0b1216191a201d2729580162cc090a403238303230303034343135413146374230323032303030303030303030303030303030303030303030303030303030304533344631384542303030303030303010bf011ab9037e585a531704034f05005408550f0e520401030f0e060d060204575101075003575a0706575500061007064e7d5c46424d1d031f071e1109034a06527b7100596f43627e7c644d437165587e760e770e637f077a7e0b1403447b5b645573507e4c78667f76505770734a5878565d5a5b575767420e1050585c4c1e657e19724343044b6a55777e615e64456b5f675e50500657525d045a7902037005007f091602004a40704d574659775167040f047a75427c59457a7d0b057942517a410b170d4f4701671d536264196e0c77406c5d4153437f5d4d1e7d18594f41790c1504481e754b5271431740575e7b5b694141445f5a03060f604d03415f7e0f1b084a676d747f1c43636317505b6f7f4f4a7d737d195269037e474706070b1403004d730f79015c4a527961546544724d4d697e01437f0c706f077977580e15044e701a075267660277401c005e055e600154461859047513771d61040810074a514b7f50417c6d7402626f0240696870036741501c454d057f74730b1707034f47700413505f447a527f415d62664a434307034d7d00435e7d4f700b1501495c45455e7a5e5f5d774657465e1d63755041557c65421c0a626d4505220478585c5d300c3a08107d79667d73161c4207312e3133322e37480350025aa90503626253513679553455644570416456324b796f566c63443936614d65626951655069595232577a73386765766d5a78357977346356614c654673564f4c4348502f484e3730302f685752635a49773065486f464e4d6a4a5a546a757a4b4455625a32516b515439614258622f6663337171724747744b72347041445370626f7965446373756c716e50563079336e655a386f4d646f4645526a544435556334707a494d3659725166545859643261514a3765345a416b7758526b76466e715043786a6363366374443370414b4d6a5345596f436a72612b45436e744263493675794772454d337049684631632b376d4554713849634e716c2f394c74714d37766c77487a6330397766504b546f746b6c4a74364e732b38777732306a38637448715678425a314a544e64515942356a364b466f4d5839577238447268707a2f39356f51754c673457472f554e4b78555a53594f6842514b4651325a79374f4c4359497430387657392f4c524a4c3157313338707a413130344b39534a7964706a51723275636b324a46546371704c723670776e6130334d6e6c413330444f684a46373344306d2b545972523756554a437051795a747958467779636f77654161417463784b2b6a667a7752327550436a524d5444634355394f354e7a502f6b3456356943596b6a3751677973623570744f68566a65564b536674474c394259714a714f6c776a646e7031736f31384139794e4a433946694a51572b33684d62376f3554724b7a6c5734624f326d45463272446e75685358642f32697a4d45706e2f6f633570414f334c6d7846375469765535525748596a64346e6a45536d36796b784b646f332b37324755586d536931792b426965726a477052554e5a3864686b3251514335396377434f6e4c714b334f76792b647673613445787973446c65654173456a4b593d880129a201050803108a03a201050804108703a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815',
    '080112a20a0a0301161d10013a0d0a044944433110b8171a024e4140024a0f01030407090a0b1216191a201d2729580162c0090a403238303230303034343135413146374230323032303030303030303030303030303030303030303030303030303030304533344631384542303030303030303010dd011ab9037e585a531704034f05005408550f0e520401030f0e060d060204575101075003575a0706575500061007064e7d5c46424d1d031f071e1109034a06527b7100596f43627e7c644d437165587e760e770e637f077a7e0b1403447b5b645573507e4c78667f76505770734a5878565d5a5b575767420e1050585c4c1e657e19724343044b6a55777e615e64456b5f675e50500657525d045a7902037005007f091602004a40704d574659775167040f047a75427c59457a7d0b057942517a410b170d4f4701671d536264196e0c77406c5d4153437f5d4d1e7d18594f41790c1504481e754b5271431740575e7b5b694141445f5a03060f604d03415f7e0f1b084a676d747f1c43636317505b6f7f4f4a7d737d195269037e474706070b1403004d730f79015c4a527961546544724d4d697e01437f0c706f077977580e15044e701a075267660277401c005e055e600154461859047513771d61040810074a514b7f50417c6d7402626f0240696870036741501c454d057f74730b1707034f47700413505f447a527f415d62664a434307034d7d00435e7d4f700b1501495c45455e7a5e5f5d774657465e1d63755041557c65421c0a626d4505220478585c5d300c3a08107d79667d73161c4207312e3133322e37480350025a9d050362625351362f726255795167416456324b796f566c54314c61726a71746b757165535463794850484539675250334147777a4a47354f6e5a6b676b72454447446351524e4c35445a4733737a3675384479336650483831446c6f577953634a6a636a53556447766f2b57524d54534842796f576f423579354d3241356568526a6d6a5a36614c594c2f506e3337633365796a49577554764572487a78512f6c3739573878386337553278712b4d6455596152767658465a3132423036334865436d706a764f757443506b3372654855776164786458324d4b76462f6f75715544586f336b757a57366f446f69587a792b662b4873524c6c65544b6243324b75545175736a334653523868786676625046735039443763665872446271556462736e697933593150684c4d4c34536a7157374148434e763357524c4e35687275367a43597778434f6e4251314b2f4c6c47686a4d54564b7656387158796d4f596d6332336532423761626e334f57686a36646a614c31386345486c3457624b516a742f3741556f384146467534397271764f2f457157593264466355364a6d316574627258432b3475486e4c6d4f786c6e753144374b714162644e2f765973702b324c4368636642356e5056333436365277542f62454b6956734c4f304b6e4161314b316234697a796b596e4231716c395043633871676c72653861446d42447636694d6d5a4a55376772717550494462727447714f4f6a615245345a63314a3432547a3045766c494957784a7749324f4d4d7833386472696d7a63514578734544392b69665555714d482b374d62586c54554c6c474e384f6a7243334b4876574b765a625938614a324d674b45385837794e46384f335771466939544235714d314655616d617271592b7575654e326b7742504d3447762f5161593da201050803108a03a201050804108703a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815',
]

# =====================================================================
# CONSTANTS
# =====================================================================
AES_KEY_LOGIN = b'Yg&tc%DEuh6%Zc^8'
AES_IV_LOGIN  = b'6oyZDr22E3ychjM%'
CLIENT_ID     = 100067
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

URL_TOKEN_GRANT    = "https://100067.connect.garena.com/oauth/guest/token/grant"
URL_TOKEN_GRANT_V2 = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
URL_DEVID          = "https://100067.msdk.garena.com/device/api/v1/android/device-id:generate"
LOGIN_HOST         = "loginbp.ppmainecoonghj.com"
RELEASE = "OB55"
REMOTE_VER = "1.132.7"

UA_MSDK  = "GarenaMSDK/4.0.44(SM-A235F ;Android 12;en;US;app 1.132.7 2019121229;)"
UA_UNITY = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"

XOR_KEY = [0,0,0,2,0,1,7,0,0,0,0,0,2,0,1,7,
           0,0,0,0,0,2,0,1,7,0,0,0,0,0,2,0]

# =====================================================================
# HELPERS
# =====================================================================
def step(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
def sign(b): return hmac.new(CLIENT_SECRET.encode(), b.encode(), hashlib.sha256).hexdigest()
def cjson(o): return json.dumps(o, separators=(",", ":"), ensure_ascii=False)
def enc_api(p): return AES.new(AES_KEY_LOGIN, AES.MODE_CBC, AES_IV_LOGIN).encrypt(pad(p, 16))
def xor_open_id(oid):
    ob = oid.encode()
    return bytes(ob[i] ^ XOR_KEY[i % 32] ^ 48 for i in range(len(ob)))

# =====================================================================
# PROTOBUF
# =====================================================================
def varint(n):
    out = b""
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out += bytes([b])
        if not n: return out

def field(n, v):
    if isinstance(v, bool): return varint((n<<3)|0) + varint(1 if v else 0)
    if isinstance(v, int):  return varint((n<<3)|0) + varint(v)
    if isinstance(v, (bytes, bytearray)): return varint((n<<3)|2) + varint(len(v)) + bytes(v)
    if isinstance(v, str):
        b = v.encode(); return varint((n<<3)|2) + varint(len(b)) + b
    if isinstance(v, dict):
        b = assemble(v); return varint((n<<3)|2) + varint(len(b)) + b
    raise TypeError(type(v))

def assemble(d):
    out = b""
    for k, v in d.items():
        if isinstance(v, list):
            for it in v: out += field(int(k), it)
        else: out += field(int(k), v)
    return out

def rv(data, pos):
    r, s = 0, 0
    while True:
        if pos >= len(data): raise ValueError("trunc")
        b = data[pos]; pos += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): return r, pos
        s += 7
        if s > 63: raise ValueError("long")

def parse(data, depth=0, maxd=6):
    pos, n = 0, len(data); out = {}
    try:
        while pos < n:
            k, pos = rv(data, pos)
            fn, w = k >> 3, k & 7
            if fn == 0: return None
            if w == 0: v, pos = rv(data, pos)
            elif w == 1:
                if pos+8 > n: return None
                v = int.from_bytes(data[pos:pos+8], "little"); pos += 8
            elif w == 2:
                sz, pos = rv(data, pos)
                if pos+sz > n: return None
                raw = data[pos:pos+sz]; pos += sz
                sub = None
                if depth < maxd and sz >= 2:
                    sub = parse(raw, depth+1, maxd)
                    if sub: v = sub
                if not sub:
                    try:
                        s_ = raw.decode("utf-8")
                        if all(32 <= ord(c) <= 126 or c in "\n\t\r" for c in s_): v = s_
                        else: v = {"_bytes": raw.hex(), "_size": sz}
                    except Exception:
                        v = {"_bytes": raw.hex(), "_size": sz}
            elif w == 5:
                if pos+4 > n: return None
                v = int.from_bytes(data[pos:pos+4], "little"); pos += 4
            else: return None
            if fn in out:
                if not isinstance(out[fn], list): out[fn] = [out[fn]]
                out[fn].append(v)
            else: out[fn] = v
        return out
    except Exception: return None

def parse_login_resp(body):
    for off in (64, 0, 4, 8, 16, 32):
        if off >= len(body): continue
        f = parse(body[off:])
        if f and len(f) >= 5: return off, f
    return None, None

def _first(v): return v[0] if isinstance(v, list) and v else v

def as_str(v):
    if isinstance(v, str): return v
    if isinstance(v, bytes): return v.decode("utf-8", "ignore")
    if isinstance(v, dict) and "_bytes" in v:
        try: return bytes.fromhex(v["_bytes"]).decode("utf-8", "ignore")
        except Exception: return None
    return None

# =====================================================================
# TICKET COUNTER PATCH
# =====================================================================
def pb_fields(buf, base=0):
    pos = 0
    while pos < len(buf):
        key_start = base + pos
        k, pos = rv(buf, pos)
        fn, w = k >> 3, k & 7
        if w == 0:
            vs = base + pos; _, pos = rv(buf, pos); yield fn, w, key_start, vs, base + pos
        elif w == 1:
            vs = base + pos; pos += 8; yield fn, w, key_start, vs, base + pos
        elif w == 2:
            sz, pos = rv(buf, pos); vs = base + pos; pos += sz; yield fn, w, key_start, vs, base + pos
        elif w == 5:
            vs = base + pos; pos += 4; yield fn, w, key_start, vs, base + pos
        else: return

def find_field(buf, base, fn_t, w_t):
    for fn, w, ks, vs, ve in pb_fields(buf, base):
        if fn == fn_t and w == w_t: return ks, vs, ve
    return None

def patch_ticket_counter(raw, counter):
    top = find_field(raw, 0, 2, 2)
    if not top: return raw
    f2 = raw[top[1]:top[2]]
    f12 = find_field(f2, 0, 12, 2)
    if not f12: return raw
    f12b = f2[f12[1]:f12[2]]
    fc = find_field(f12b, 0, 2, 0)
    if not fc: return raw
    ks = top[1] + f12[1] + fc[0]
    ve = top[1] + f12[1] + fc[2]
    return raw[:ks] + bytes([0x10]) + varint(counter) + raw[ve:]

# =====================================================================
# HTTP
# =====================================================================
def token_grant(s, uid, password):
    h = {"Host": "100067.connect.garena.com", "User-Agent": UA_MSDK,
         "Content-Type": "application/x-www-form-urlencoded",
         "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
    r = s.post(URL_TOKEN_GRANT, data={
        "uid": str(uid), "password": password, "response_type": "token",
        "client_type": "2", "client_secret": CLIENT_SECRET, "client_id": str(CLIENT_ID),
    }, headers=h, timeout=(5,15))
    step(f"token:grant(form) -> {r.status_code}")
    if r.status_code == 200:
        try:
            d = r.json()
            if "access_token" in d: return d["access_token"], d["open_id"]
        except Exception: pass
    body = cjson({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                  "client_type": 2, "device_id": "", "password": password,
                  "response_type": "token", "uid": uid})
    h2 = {"User-Agent": UA_MSDK, "Accept": "application/json",
          "Content-Type": "application/json; charset=utf-8",
          "Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
    r = s.post(URL_TOKEN_GRANT_V2, data=body.encode(), headers=h2, timeout=(5,15))
    step(f"token:grant(v2) -> {r.status_code}")
    d = r.json()
    if "access_token" not in d.get("data", {}): raise Exception(f"token:grant failed: {d}")
    dd = d.get("data", d)
    return dd["access_token"], dd["open_id"]

def device_id_generate(s):
    body = cjson({"app_id": CLIENT_ID, "data": {
        "ad_aaid": "", "android_id": "560e01b961cdd0d2",
        "android_version_release": "12", "android_version_sdk": "31",
        "brand": "OnePlus", "build_date": "1788961904000",
        "build_display": "SP1A.210812.016 release-keys", "build_id": "SP1A.210812.016",
        "cpu_abis": "arm64-v8a,armeabi-v7a,armeabi",
        "drm_id": "991b990d9ca5195f15bc298eada8056ec3115d9211c20fecdaf8376a4caffde5",
        "drm_vendor": "Google",
        "fingerprint": "OnePlus/GM1910/GM1910:12/SP1A.210812.016/1660123456:user/release-keys",
        "gcbooster_uuid": "", "hardware": "qcom", "imei": "", "key_mqs_uuid": "",
        "model": "GM1910", "product_name": "GM1910",
        "random_uuid": "0a98e0de-fc49-4177-ae98-4d5c4b8c1cea",
        "soc_manufacturer": "Qualcomm", "soc_model": "SM8150"}})
    h = {"User-Agent": UA_MSDK, "Authorization": f"Signature {sign(body)}",
         "Accept": "application/json", "Content-Type": "application/json; charset=utf-8",
         "Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
    try: s.post(URL_DEVID, data=body.encode(), headers=h, timeout=(5,15))
    except Exception: pass

def build_majorlogin_body(at, oid, region):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    return assemble({
        3: now, 4: "free fire", 5: 1, 7: REMOTE_VER,
        8: "Android OS 12 / API-31 (SP1A.210812.016)", 9: "Handheld",
        10: "CHINA MOBILE", 11: "WIFI", 12: 960, 13: 540, 14: "220",
        15: "ARM64 FP ASIMD AES | 2301 | 8", 16: 3932,
        17: "Adreno (TM) 640", 18: "OpenGL ES 3.2 v334 O",
        19: f"Google|{oid[:8]}-ec24-4235-aef1-09d4515808e7",
        20: "57.154.5.33", 21: "en", 22: oid, 23: "4", 24: "Handheld",
        25: "OnePlus GM1910", 26: region.upper(),
        29: at, 30: 1, 41: "CHINA MOBILE", 42: "WIFI",
        57: "00000000000000000000000000000000",
        60: 128929, 61: 121228, 62: 2104,
        64: 127798, 65: 128929, 66: 127798, 67: 128929,
        70: 4, 73: 3,
        74: "/data/app/com.dts.freefireth/lib/arm64", 76: 1,
        77: "0000000000000000|/data/app/com.dts.freefireth/base.apk",
        78: 6, 79: 2, 81: "64", 83: "2019121229", 85: 3,
        86: "OpenGLES2", 87: 511, 88: 4, 92: 61975, 93: "3rd_party",
        94: "KqsHT4Uz1H4RYSwtBITC+rOY8PREUv622Lv+xuaiIHpbkYX+LWG1405kd2AOEVzWEpMCvbW8vteVHx4R1lVir1ndiMysQzxNmZBW4WHga3PJuigq",
        95: 111107, 96: '{"cur_rate":null,"support_etc2":false}',
        97: 1, 98: 1, 99: "4", 100: "100", 104: 43955, 105: 1,
        106: "https://dl.cdn.freefiremobile.com/live/ABHotUpdates/|https://dl-core.cdn.freefiremobile.com/live/ABHotUpdates/|4a0070ac356973792f002e0b25b96c3b",
        107: "c8e41b7a93f02d56e1a94c7b8203f5d1"})

def call_major_login(s, at, oid, region):
    h = {"Host": LOGIN_HOST, "User-Agent": UA_UNITY, "Accept": "*/*",
         "Accept-Encoding": "deflate, gzip", "X-GA-SV": str(int(time.time())),
         "Authorization": "Bearer", "X-GA": "v1 1", "ReleaseVersion": RELEASE,
         "Content-Type": "application/x-www-form-urlencoded",
         "X-Unity-Version": "2018.4.12f1"}
    return s.post(f"https://{LOGIN_HOST}/MajorLogin",
                  data=enc_api(build_majorlogin_body(at, oid, region)),
                  headers=h, timeout=(5,15))

def get_login_data(s, jwt, oid, host, region):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    body = assemble({
        3: now, 4: "free fire", 5: 1, 7: REMOTE_VER,
        8: "Android OS 12 / API-31 (SP1A.210812.016)", 9: "Handheld",
        10: "Vi India", 11: "WIFI", 12: 1600, 13: 720, 14: "320",
        15: "ARM64 FP ASIMD AES | 2301 | 8", 16: 2799,
        17: "Adreno (TM) 640", 18: "OpenGL ES 3.2 build 1.1@5425693",
        19: f"Google|{oid[:8]}-b10c-454a-852d-06332cd498eb",
        20: "27.59.69.226", 21: "en", 22: oid, 23: "4",
        24: "Handheld", 25: "OnePlus GM1910", 26: region.upper(),
        29: jwt, 30: 1})
    h = {"Host": host, "User-Agent": UA_UNITY, "Accept": "*/*",
         "Accept-Encoding": "deflate, gzip", "X-GA-SV": str(int(time.time())),
         "Authorization": f"Bearer {jwt}", "X-GA": "v1 1",
         "ReleaseVersion": RELEASE, "Content-Type": "application/x-www-form-urlencoded",
         "X-Unity-Version": "2018.4.12f1"}
    r = s.post(f"https://{host}/GetLoginData", data=enc_api(body), headers=h, timeout=(5,15))
    return r.status_code, r.content

def extract_keys(fields):
    def hx(v):
        v = _first(v)
        if isinstance(v, bytes): return v.hex()
        if isinstance(v, dict) and "_bytes" in v: return v["_bytes"]
        return v
    return {"jwt": _first(fields.get(8)), "kts": _first(fields.get(21)),
            "ak": hx(fields.get(22)), "aiv": hx(fields.get(23)),
            "server_url": _first(fields.get(10))}

def extract_account_id(jwt_str):
    try:
        p = jwt_str.split(".")[1]; p += "=" * ((4 - len(p) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(p)).get("account_id")
    except Exception: return None

# =====================================================================
# SOCKET
# =====================================================================
AK = None; AIV = None; ACCOUNT_ID = 0
whisper_sock = None; online_sock = None
stop_event = threading.Event()
pong_count = [0]; match = [None]; group_id = [None]
online_alive = [False]; whisper_alive = [False]
got_28 = threading.Event()
init_1_plain = [None]; init_2_plain = [None]; confirm_plain = [None]
TICKETS = []

def aes_enc(p, k, iv): return AES.new(k, AES.MODE_CBC, iv).encrypt(pad(p, 16))

def hs_whisper(jwt, acc, kts, k, iv):
    e = aes_enc(bytes.fromhex(jwt.encode().hex()), k, iv)
    return (b"\x8c\x16" + acc.to_bytes(8,"big") + kts.to_bytes(4,"big")
            + b"\x00\x00" + len(e).to_bytes(2,"big") + e)

def hs_online(jwt, acc, kts, k, iv):
    e = aes_enc(bytes.fromhex(jwt.encode().hex()), k, iv)
    return (b"\x8e\x16" + acc.to_bytes(8,"big") + kts.to_bytes(4,"big")
            + b"\x00"*5 + len(e).to_bytes(3,"big") + e)

def pkt_pong(acc, k, iv):
    p = assemble({1: acc, 2: 5, 3: 2}); e = aes_enc(p, k, iv)
    return b"\x05\x15" + len(e).to_bytes(4,"big") + e

def pkt_presence(mode, k, iv):
    inner = assemble({2: mode, 3: "en"}); outer = assemble({1: 3, 2: inner})
    e = aes_enc(outer, k, iv)
    return b"\x12\x16" + len(e).to_bytes(4,"big") + e

def pkt_2816(plain, k, iv):
    e = aes_enc(plain, k, iv); return b"\x28\x16" + len(e).to_bytes(4,"big") + e

def pkt_1d16(plain, k, iv):
    e = aes_enc(plain, k, iv); return b"\x1d\x16" + len(e).to_bytes(4,"big") + e

def pkt_0316(plain, k, iv):
    e = aes_enc(plain, k, iv); return b"\x03\x16" + len(e).to_bytes(4,"big") + e

def pkt_0e16(plain, k, iv):
    e = aes_enc(plain, k, iv); return b"\x0e\x16" + len(e).to_bytes(4,"big") + e

def pkt_ping(): return b"\x02\x16"

def parse_match_assign(raw):
    if len(raw) < 6 or raw[0] != 0x03: return None
    p = parse(raw[5:])
    if not p or 5 not in p: return None
    inner = p[5]
    if not isinstance(inner, dict): return None
    addr = as_str(_first(inner.get(2))); sec = as_str(_first(inner.get(3)))
    if not addr or not sec: return None
    return {"match_id": _first(inner.get(1)), "server_addr": addr, "secret": sec,
            "prepare_jwt": as_str(_first(inner.get(4))), "mode": _first(p.get(4))}

def extract_messages(buf):
    msgs = []
    while True:
        if len(buf) < 5: break
        b0 = buf[0]; b1 = buf[1] if len(buf) > 1 else 0
        two = (b0==0x02 and b1==0x16) or (b0==0x12 and b1==0x16) or \
              (b0==0x28 and b1==0x16) or (b0==0x1d and b1==0x16) or \
              (b0==0x03 and b1==0x16) or (b0==0x05 and b1==0x15) or \
              (b0==0x0e and b1==0x16)
        if two:
            if len(buf) < 6: break
            ln = int.from_bytes(buf[2:6], "big"); total = 6 + ln
        else:
            ln = int.from_bytes(buf[1:5], "big"); total = 5 + ln
        if len(buf) < total: break
        msgs.append(buf[:total]); buf = buf[total:]
    return msgs, buf

def handle_msg(name, sock, msg):
    if not msg: return
    op1 = msg[0]; op2 = msg[1] if len(msg) > 1 else 0
    if op2 in (0x16, 0x15): return

    if op1 == 0x05:
        if online_alive[0]:
            try:
                sock.send(pkt_pong(ACCOUNT_ID, AK, AIV))
                pong_count[0] += 1
                if pong_count[0] % 20 == 0: step(f"[{name}] pongs: {pong_count[0]}")
            except Exception: pass

    elif op1 == 0x12:
        try:
            txt = msg[5:].decode("utf-8", "ignore")
            m = re.search(r'"GroupID":(\d+)', txt)
            if m and group_id[0] is None:
                group_id[0] = int(m.group(1))
                step(f"[QUEUE] GroupID = {group_id[0]}")
        except Exception: pass

    elif op1 == 0x28:
        p = parse(msg[5:]) or {}
        f4 = p.get(4) if isinstance(p, dict) else None
        if not got_28.is_set():
            got_28.set()
            step(f"[28] received (f4={f4})")
            threading.Thread(target=pcap_after_28, args=(sock,), daemon=True).start()

    elif op1 == 0x03:
        p = parse(msg[5:])
        t = p.get(4) if isinstance(p, dict) else None
        step(f"[03] type={t} len={len(msg)}")
        m = parse_match_assign(msg)
        if m and match[0] is None:
            step("=" * 60)
            step(f"[MATCH] match_id    = {m['match_id']}")
            step(f"[MATCH] server_addr = {m['server_addr']}")
            step(f"[MATCH] secret      = {m['secret']}")
            step("=" * 60)
            match[0] = m

    elif op1 == 0x0b:
        step(f"[{name}] KICK op=0b payload={msg[5:25].hex()}")

def recv_loop(name, sock):
    buf = b""
    sock.settimeout(1.0)
    while not stop_event.is_set():
        try: data = sock.recv(65536)
        except socket.timeout:
            try:
                msgs, buf = extract_messages(buf)
                for m in msgs: handle_msg(name, sock, m)
            except Exception: pass
            continue
        except Exception:
            if name == "online": online_alive[0] = False
            else: whisper_alive[0] = False
            break
        if not data:
            if name == "online": online_alive[0] = False
            else: whisper_alive[0] = False
            break
        buf += data
        try:
            msgs, buf = extract_messages(buf)
            for m in msgs: handle_msg(name, sock, m)
        except Exception: buf = b""

def online_init_sequence():
    global online_sock
    time.sleep(0.693)
    try:
        p = pkt_2816(init_1_plain[0], AK, AIV)
        online_sock.send(p); step(f"[online] T+0.69s init_1 {len(p)}B")
    except Exception as e: step(f"[online] init_1 err: {e}"); return
    time.sleep(0.810)
    try:
        p = pkt_2816(init_2_plain[0], AK, AIV)
        online_sock.send(p); step(f"[online] T+1.50s init_2 {len(p)}B")
    except Exception as e: step(f"[online] init_2 err: {e}"); return
    time.sleep(0.003)
    try:
        inner = assemble({1: 3, 2: "2019121229", 3: 2, 4: 1})
        outer = assemble({1: 6, 2: inner})
        p = pkt_1d16(outer, AK, AIV)
        online_sock.send(p); step(f"[online] T+1.51s init_3 {len(p)}B")
    except Exception as e: step(f"[online] init_3 err: {e}"); return
    step("[online] init done — waiting for 28")

def sleep_i(sec):
    end = time.time() + sec
    while time.time() < end:
        if stop_event.is_set() or match[0]: return False
        time.sleep(0.2)
    return True

def pcap_after_28(sock):
    try:
        time.sleep(3.683)
        p1 = pkt_0316(confirm_plain[0], AK, AIV)
        sock.send(p1); step(f"[online] T+3.68s sent 0316 confirm wire={len(p1)}B")
        time.sleep(2.058)
        sock.send(pkt_ping()); step("[online] T+5.74s sent 0216 ping")
        time.sleep(1.870)
        p3 = pkt_0e16(assemble({1: 32}), AK, AIV)
        sock.send(p3); step(f"[online] T+7.61s sent 0e16 wire={len(p3)}B")
    except Exception as e:
        step(f"[online] after28 err: {e}")

def ticket_loop():
    if not got_28.wait(30):
        step("[ticket] no 28 in 30s"); return
    if not TICKETS:
        step("[ticket] TICKETS_HEX empty"); return
    idx = min(4, len(TICKETS)-1)
    ticket = TICKETS[idx]
    step(f"[ticket] using ticket idx={idx} {len(ticket)}B")
    if not sleep_i(3.7): return
    try:
        online_sock.send(pkt_0316(ticket, AK, AIV))
        step(f"[ticket] sent raw ({len(ticket)}B pt)")
    except Exception as e:
        step(f"[ticket] err: {e}"); return
    cnt = 222
    while not stop_event.is_set() and online_alive[0] and match[0] is None:
        if not sleep_i(25): return
        try:
            t = patch_ticket_counter(ticket, cnt)
            online_sock.send(pkt_0316(t, AK, AIV))
            step(f"[ticket] sent counter={cnt}")
        except Exception as e:
            step(f"[ticket] err: {e}"); return
        cnt += 1

def ping_whisper():
    while not stop_event.is_set() and whisper_alive[0]:
        try: whisper_sock.send(pkt_ping())
        except Exception: return
        for _ in range(2):
            if stop_event.is_set(): return
            time.sleep(1)

def queue_loop(modes, k, iv):
    for _ in range(80):
        if stop_event.is_set(): return
        time.sleep(0.1)
    for mode in modes:
        if stop_event.is_set() or match[0]: return
        try:
            if whisper_alive[0]:
                whisper_sock.send(pkt_presence(mode, k, iv))
                step(f"[queue] presence mode={mode}")
        except Exception: return
        time.sleep(2)
    last = time.time()
    while not stop_event.is_set() and match[0] is None:
        if time.time() - last > 45 and whisper_alive[0]:
            try:
                whisper_sock.send(pkt_presence(modes[0], k, iv))
                step(f"[queue] resent mode={modes[0]}"); last = time.time()
            except Exception: return
        time.sleep(1)

def stats_loop(start):
    while not stop_event.is_set():
        for _ in range(15):
            if stop_event.is_set(): return
            time.sleep(1)
        step(f"[stats] t={int(time.time()-start)}s wA={whisper_alive[0]} oA={online_alive[0]} "
             f"pongs={pong_count[0]} grp={group_id[0]} match={'YES' if match[0] else 'no'}")

# =====================================================================
# MAIN
# =====================================================================
def main():
    global whisper_sock, online_sock, AK, AIV, ACCOUNT_ID, TICKETS

    init_1_plain[0]  = bytes.fromhex(INIT_1_HEX)
    init_2_plain[0]  = bytes.fromhex(INIT_2_HEX)
    confirm_plain[0] = bytes.fromhex(CONFIRM_HEX)
    TICKETS = [bytes.fromhex(h) for h in TICKETS_HEX if h]

    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="IND")
    ap.add_argument("--duration", type=int, default=300)
    ap.add_argument("--uid", type=int, required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--modes", default="2,5,11")
    ap.add_argument("--out", default="result.json")
    args = ap.parse_args()

    step(f"[cfg] init_1={len(init_1_plain[0])}B  init_2={len(init_2_plain[0])}B  confirm={len(confirm_plain[0])}B")
    step(f"[cfg] tickets={len(TICKETS)} sizes={[len(t) for t in TICKETS]}")

    if not TICKETS:
        step("[FATAL] TICKETS_HEX empty"); return 1

    region = args.region.upper()
    s = requests.Session(); s.verify = False
    uid = args.uid; password = args.password

    step("=== LOGIN ===")
    at, oid = token_grant(s, uid, password)
    step(f"access_token={at[:20]}...  open_id={oid}")
    device_id_generate(s)

    r = call_major_login(s, at, oid, region)
    step(f"MajorLogin HTTP {r.status_code} len={len(r.content)}")
    if r.status_code != 200: return 1
    off, fields = parse_login_resp(r.content)
    if not fields: return 1
    keys = extract_keys(fields)
    jwt = keys["jwt"]; jwt = jwt.decode("utf-8","ignore") if isinstance(jwt, bytes) else jwt
    surl = keys["server_url"]; surl = surl.decode("utf-8","ignore") if isinstance(surl, bytes) else surl
    AK = bytes.fromhex(keys["ak"]); AIV = bytes.fromhex(keys["aiv"])
    ACCOUNT_ID = extract_account_id(jwt); kts = keys["kts"]
    step(f"account_id={ACCOUNT_ID}  kts={kts}")

    host = surl.replace("https://","").rstrip("/")
    gl_code, gl_body = get_login_data(s, jwt, oid, host, region)
    step(f"GetLoginData HTTP {gl_code} len={len(gl_body)}")
    if gl_code != 200: return 1
    gl = parse(gl_body)
    if not gl: return 1

    whisper_addr = as_str(gl.get(32)); online_addr = as_str(gl.get(14))
    step(f"whisper={whisper_addr}  online={online_addr}")
    w_ip, w_port = whisper_addr.rsplit(":", 1); w_port = int(w_port)
    o_ip, o_port = online_addr.rsplit(":", 1);  o_port = int(o_port)

    hs_w = hs_whisper(jwt, ACCOUNT_ID, kts, AK, AIV)
    hs_o = hs_online(jwt, ACCOUNT_ID, kts, AK, AIV)

    step("=== CONNECT whisper ===")
    whisper_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    whisper_sock.settimeout(10)
    whisper_sock.connect((w_ip, w_port)); whisper_sock.send(hs_w)
    whisper_alive[0] = True; step("[whisper] handshake sent")

    step("=== CONNECT online ===")
    online_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    online_sock.settimeout(10)
    online_sock.connect((o_ip, o_port)); online_sock.send(hs_o)
    online_alive[0] = True; step("[online] handshake sent")

    start = time.time()
    threading.Thread(target=recv_loop, args=("whisper", whisper_sock), daemon=True).start()
    threading.Thread(target=recv_loop, args=("online", online_sock), daemon=True).start()
    threading.Thread(target=online_init_sequence, daemon=True).start()
    threading.Thread(target=ticket_loop, daemon=True).start()
    threading.Thread(target=ping_whisper, daemon=True).start()
    threading.Thread(target=stats_loop, args=(start,), daemon=True).start()
    modes = [int(x) for x in args.modes.split(",") if x.strip()]
    threading.Thread(target=queue_loop, args=(modes, AK, AIV), daemon=True).start()

    step(f"running {args.duration}s")
    try:
        for _ in range(args.duration):
            if stop_event.is_set() or match[0]: break
            time.sleep(1)
    except KeyboardInterrupt: pass

    stop_event.set()
    for sk in (whisper_sock, online_sock):
        if sk:
            try: sk.close()
            except: pass

    with open(args.out, "w") as f:
        json.dump({"uid": uid, "account_id": ACCOUNT_ID,
                   "ak": AK.hex(), "aiv": AIV.hex(), "kts": kts,
                   "group_id": group_id[0], "match": match[0],
                   "pongs": pong_count[0],
                   "whisper_alive": whisper_alive[0], "online_alive": online_alive[0]}, f, indent=2)

    if match[0]:
        step(f"MATCH: id={match[0]['match_id']} srv={match[0]['server_addr']} secret={match[0]['secret']}")
    else:
        step(f"NO MATCH grp={group_id[0]} pongs={pong_count[0]} wA={whisper_alive[0]} oA={online_alive[0]}")
    return 0

if __name__ == "__main__":
    try: sys.exit(main())
    except KeyboardInterrupt: sys.exit(130)
    except Exception as e: print(f"\n[!] fatal: {e}"); sys.exit(1)
