#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#Python3 ile kodlanmıştır.
#Author: Alparslan Özdemir.
#Windows'da sorunsuz çalışmaktadır. Kali Linux'da çalıştırıldığında ise subnetlerde bazen hatalı sonuç verebilmektedir.
import socket
import sys
import struct
import ipaddress #Subnetleri ve ipleri python'un kendi kütüphanesine hesaplatıyorum. 
import time

icmp_tipi=8
icmp_kodu=0
icmp_soketkodu = socket.getprotobyname('icmp')  #ICMP Paketini üretmek için gerekli değerleri daha açık olması için programın en üstünde türkçe şekilde tanımladım.
soket=socket.socket(socket.AF_INET,socket.SOCK_RAW, icmp_soketkodu)     #ICMP paketleri için uygun bir soket oluşturuyor.
def checksum(source_string):
##        # ICMP paketinin 16 bitlik 1 e tümleyenini (sum'unu) hesaplıyormuş. Hazır aldım.
        sum = 0
        count_to = (len(source_string) / 2) * 2
        count = 0
        while count < count_to:
            this_val = source_string[count + 1]*256+source_string[count]
            sum = sum + this_val
            sum = sum & 0xffffffff
            count = count + 2
        if count_to < len(source_string):
            sum = sum + source_string[len(source_string) - 1]
            sum = sum & 0xffffffff
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer
def paket_uret():
    # b = unsigned char (8 bit) H=Unsigned Short(16 bit) Toplam 64 bit headeri struct kullanarak oluşturuyoruz.
    paket = struct.pack('!bbHHH', icmp_tipi, icmp_kodu, 0, 0, 1) # Checksum ve ID ini 0, sequence number'ini 1 olarak belirliyoruz. Daha sum unu hesaplatmadık.
    #Checksum u 0 olan bir kukla header oluşturuyoruz. Şimdi sum u hesaplatıp paketi tekrar sum ile oluşturacağız..
    sum=checksum(paket) # bu sum u mevcut kuklaya eklemektense, yeniden oluşturmak daha kolay olduğu için bütün kaynaklar bu şekilde yapmış.
    paket = struct.pack('!bbHHH', icmp_tipi, icmp_kodu, sum, 0, 1)
    return paket
def pingat(ip):
        try:    #ip'yi çözümleyemeyip soketten gaierror dönerse program çökmesin. ( Get Address Info Error )
                soket.settimeout(1.5)   #ping paketinin gidiş geliş sürelerini falan da gösteren bir program yapmak istedim ama baktım işin içinden çıkılmaz bir hal alıyor, soket timeoutu kullandım.
                soket.sendto(paket_uret(), (ip,0))#belirtilen soketten belirtilen paketi belirtilen ip'ye belirtilen porttan gönderir. ICMP'de port olmadığı için 0 girdim.
                try:
                        alinan_paket, adresi=soket.recvfrom(1024) #Soketten dönüş almayı deniyor. recevie den geliyor recv.
                        icmp_headeri = alinan_paket[20:28]
                        alinantip, alinankod, alinanchecksum, alinanid, alinansequence = struct.unpack('bbHHH', icmp_headeri)
                        if alinantip==0: #echo reply paketlerinin icmp tipi 0'dır. Bu yüzden paket dönse bile dönen paket 0 seğilse hedef aktif değildir. bazen tip-
                            print(ip + " ---> AKTİF !!")  #3 paketler dönebiliyor. Bu paketler unreachable paketleri olabiliyor ve program bunları aktif sanabiliyor.
                        else:
                            print(ip + " ---> AKTİF DEĞİL.")
                except socket.timeout:  #1.5 Saniye timeout süresi içerisinde hiçbir paket dönmeyip de soket timeout a düşerse yine aktif değildir.
                        print(ip + " ---> AKTİF DEĞİL.")
        except:
                print("Geçerli bir adres girdiğine emin misin? Adresi çözümleyemedim.")  #Yeterince açık :)


if __name__== "__main__": #Python'da bir main fonksiyonu tanımlama biçimi.
        #programı Python3 ile yazdım.. Dolayısı ile eğer python 2 ile çalışırsa hata veriyor.Ben de hiç hataya girmeden direkt bir sürüm kontrolü sağlıyorum ve eğer python 3 değilse uyarı verdirip çıkış yaptırıyorum.
    Python2metni = """
Python'ın 2.x sürümlerinden birini kullanıyorsunuz.
Programı çalıştırabilmek için sisteminizde Python'ın
3.x sürümlerinden biri kurulu olmalı.
Eğer Terminalde çalışıyorsanız \033[1m python yerine python3\033[0m
komutunu vermeyi deneyebilirsiniz."""
    try:
        if sys.version_info.major < 3:#Burası pyton sürümünün 3 olup olmadığını denetliyor.
            print(Python2metni) #3den düşük bir sürümse belirtilen hatayı verip çıkış yapıyor.
            exit()
    except AttributeError: #Bu da python 2.7 den bile düşükse çalışan kısım.
        print(Python2metni)
        exit()
    if len(sys.argv) < 2: #argüman girilip girilmediğini kontrol ediyor.
        print('kullanim: "python pingat.py subnet/ip/domain"')
    else:
        try:
            ip=(ipaddress.ip_network(sys.argv[1])) #Girilen argümanı burada alıyoruz ve subnet girildiyse çözdürüyoruz :))
            for hedef in ip: #Subnet ise subnetteki her ip'yi, normal ip girildi ise o ip'yi ping yi pingat fonksiyonuna hedef olarak gönderip ping attırıyoruz.
                pingat(str(hedef))
        except ValueError: #Eğer ip yerine domain girilmişse, bu ip kontrolü değer hatası döndürüyor çünkü domain bir ip ya da subnet değildir.
            hedef=(sys.argv[1]) #Domain girildiği takdirde hiçbir şekilde subnet kontrolü yapmadan direkt domaini hedef olarak yolluyor.
            pingat(hedef)

