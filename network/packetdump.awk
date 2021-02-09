#!/usr/bin/awk -f

# tcpdump -xx -i eth1
#06:45:29.151184 00:00:00:05:81:01 (oui Ethernet) > 00:00:00:00:81:01 (oui Ethernet), ethertype Unknown (0x8200), length 144: [63/3323]
        #0x0000:  0000 0000 8101 0000 0005 8101 8200 a3e8
        #0x0010:  1800 0000 0000 0000 0074 0000 0000 0000
        #0x0020:  0000 0000 0000 0000 0000 0000 0001 0000
        #0x0030:  0000 0000 0000 0000 0000 011b 1900 0000
        #0x0040:  9886 5df5 5bac 88f7 0902 0036 1800 0000
        #0x0050:  0000 0399 205a 0000 0000 0000 0000 0000
        #0x0060:  0000 0001 0001 b5cf 03fc 0000 5da4 11b5
        #0x0070:  0d41 4710 9886 5dff 01f5 5bac 0001 01aa
        #0x0080:  0002 0000 dae9 e5b0 15cc ffff fc66 dfa6
#06:45:29.179217 00:00:00:05:81:01 (oui Ethernet) > 00:00:00:00:81:01 (oui Ethernet), ethertype Unknown (0x8200), length 118:
        #0x0000:  0000 0000 8101 0000 0005 8101 8200 a3e8
        #0x0010:  1800 0000 03fb 0002 1588 25d6 b990 0000
        #0x0020:  0370 0180 c200 0000 0000 0000 0000 0000
        #0x0030:  0000 0000 0000 0000 0000 0180 c200 0002
        #0x0040:  0000 0000 002b 8809 0a00 19a7 0001 1000
        #0x0050:  0000 0100 0402 0000 0000 0000 0000 0000
        #0x0060:  0000 0000 0000 0000 0000 0000 0000 0000
        #0x0070:  0000 0000 0000
#06:45:29.179231 00:00:00:05:81:01 (oui Ethernet) > 00:00:00:00:81:01 (oui Ethernet), ethertype Unknown (0x8200), length 136:
        #0x0000:  0000 0000 8101 0000 0005 8101 8200 a3e8
        #0x0010:  1800 0000 0000 0000 006c 0000 0000 0000
        #0x0020:  0000 0000 0000 0000 0000 0000 0001 0000
        #0x0030:  0000 0000 0000 0000 0000 011b 1900 0000
        #0x0040:  9886 5df5 5bac 88f7 0002 002c 1800 0000
        #0x0050:  1155 1fcf 6f7e 0000 0000 0000 0000 0000
        #0x0060:  0000 0001 0001 7de4 00fc 0000 5da4 11b5
        #0x0070:  0eed 58a1 0000 01aa 0002 0000 dc95 f7b0
        #0x0080:  15cc eeaa e030 9082
#06:45:29.179234 00:00:00:05:81:01 (oui Ethernet) > 00:00:00:00:81:01 (oui Ethernet), ethertype Unknown (0x8200), length 154:
        #0x0000:  0000 0000 8101 0000 0005 8101 8200 a3e8
        #0x0010:  1800 0000 0000 0000 007e 0000 0000 0000
        #0x0020:  0000 0000 0000 0000 0000 0000 0001 0000
        #0x0030:  0000 0000 0000 0000 0000 011b 1900 0000
        #0x0040:  9886 5df5 5bac 88f7 0b02 0040 1800 003c
        #0x0050:  0000 0000 0000 0000 0000 0000 0000 0000
        #0x0060:  0000 0001 0001 3ef2 05fd 0000 0000 0000
        #0x0070:  0000 0000 0025 0080 0621 ffff 8000 0000
        #0x0080:  0000 0000 0100 00a0 01aa 0002 0000 dc96
        #0x0090:  2440 15cd 0000 0000 0000
#16:21:41.508098 00:00:00:05:81:01 (oui Ethernet) > 00:00:00:00:81:01 (oui Ethernet), ethertype Unknown (0x8200), length 140:
        #0x0000:  0000 0000 8101 0000 0005 8101 8200 a3e8
        #0x0010:  1800 1224 0000 0000 0070 0000 0000 0000
        #0x0020:  0000 0000 0000 0000 0000 0000 0001 0000
        #0x0030:  0000 0000 0000 0000 0000 011b 1900 0000
        #0x0040:  a000 0000 0001 88a8 0bbc 88f7 0b02 0040
        #0x0050:  1800 003c 0000 0000 0000 0000 0000 0000
        #0x0060:  0000 0000 0000 0001 0001 8a9d 05fd 0000
        #0x0070:  0000 0000 0000 0000 0025 0080 0621 ffff
        #0x0080:  8000 0000 0000 0000 0100 00a0
#01:44:29.664089 00:00:00:05:81:01 (oui Ethernet) > 00:00:00:00:81:01 (oui Ethernet), ethertype Unknown (0x8200), length 144:
        #0x0000:  0000 0000 8101 0000 0005 8101 8200 a3e8
        #0x0010:  1800 1224 0000 0000 0074 0000 0000 0000
        #0x0020:  0000 0000 0000 0000 0000 0000 0001 0000
        #0x0030:  0000 0000 0000 0000 0000 011b 1900 0000
        #0x0040:  7c41 a28d 6cb7 88a8 ebe0 8100 e066 88f7
        #0x0050:  0b02 0040 1800 003c 0000 0000 0000 0000
        #0x0060:  0000 0000 7c41 a2ff 018d 6cab 0002 0bb0
        #0x0070:  05fd 0000 0000 0000 0000 0000 0025 0080
        #0x0080:  0621 ffff 8000 0000 0000 0000 0100 01a0


BEGIN {
    cmic_len = 58
    start = 0
    offset = 0
    begin_time = systime()
}

/ethertype.*length/ {
    pkt_time = $1
    if (index($NF,":") > 0) {
        lengthfield = $NF
    }
    else {
        lengthfield = $(NF-1)
    }
    sub(/:.*/,"",lengthfield) # remove ":" in length field
    pkt_length = strtonum(lengthfield)/2
    start = 1
    offset = 0
    next
}

{
    if (start) {
        for (i = 2; i < 10; i++) {
            pkt[offset++] = $i
            if (offset >= pkt_length) {
                start = 0
                offset = 0
                break
            }
        }
        if (!start) {
            if (pkt[cmic_len/2 + 6] == "8100" || pkt[cmic_len/2 + 6] == "88a8")
            {
                if (pkt[cmic_len/2 + 8] == "8100" || pkt[cmic_len/2 + 8] == "88a8")
                    eth_type_offset = cmic_len/2 + 10
                else
                    eth_type_offset = cmic_len/2 + 8
            }
            else
            {
                eth_type_offset = cmic_len/2 + 6
            }
            if (pkt[eth_type_offset] == "88f7") {
                dumpPTP(pkt)
            } else if (pkt[eth_type_offset] == "8902") {
                dumpCFM(pkt)
            } else if (pkt[eth_type_offset] == "8809") {
                subtype = rshift(strtonum("0x"pkt[eth_type_offset+1]),8)
                if (subtype == 0xa) {
                    dumpSYNCE(pkt)
                }
                else if (subtype == 0x1) {
                    dumpLAG(pkt)
                }
            }
        }
    }
}

END {
    printf "Packets Received in %d seconds\n", systime() - begin_time
    printf "--------------------------------\n"
    for (msg in ptp_counter) {
        printf "%s\t%d\n", ptp_msg_type[msg], ptp_counter[msg]
    }
    if (synce_counter > 0) printf "SYNCE\t%d\n", synce_counter
}

function dumpMac(pkttype, pkt)
{
    for (i = 0; i < 3; i++) {
        val = strtonum("0x"pkt[cmic_len/2+i])
        dst[2*i] = rshift(val,8)
        dst[2*i+1] = and(val,0xFF)
    }
    for (i = 0; i < 3; i++) {
        val = strtonum("0x"pkt[cmic_len/2+i+3])
        src[2*i] = rshift(val,8)
        src[2*i+1] = and(val,0xFF)
    }
    printf "%s\tTime\t%s\n", pkttype, pkt_time
    printf "%s\tMac\t%02x:%02x:%02x:%02x:%02x:%02x -> %02x:%02x:%02x:%02x:%02x:%02x\n",
            pkttype,
            src[0], src[1], src[2], src[3], src[4], src[5],
            dst[0], dst[1], dst[2], dst[3], dst[4], dst[5]
    svid = 0
    cvid = 0
    if (pkt[cmic_len/2 + 6] == "8100" || pkt[cmic_len/2 + 6] == "88a8") {
        if (pkt[cmic_len/2 + 8] == "8100" || pkt[cmic_len/2 + 8] == "88a8") {
            svid = and(strtonum("0x"pkt[cmic_len/2 + 7]), 0xFFF)
            cvid = and(strtonum("0x"pkt[cmic_len/2 + 9]), 0xFFF)
        }
        else {
            cvid = and(strtonum("0x"pkt[cmic_len/2 + 7]), 0xFFF)
        }
    }
    printf "%s\tSVID\t%d\n", pkttype, svid
    printf "%s\tCVID\t%d\n", pkttype, cvid
}

function dumpPTP(ptp)
{
    msg_offset = eth_type_offset + 1
    ptp_body_offset = msg_offset + 17
    ptp_tlv_delay_offset = 3
    ptp_tlv_timestamp_offset = 5
    ptp_msg_type[0] = "SYNC"
    ptp_msg_type[1] = "REQ"
    ptp_msg_type[8] = "FLOW"
    ptp_msg_type[9] = "RESP"
    ptp_msg_type[11] = "ANNO"
    msg_type = and(rshift(strtonum("0x"ptp[msg_offset]),8), 0xF)
    ptp_domain = and(strtonum("0x"ptp[msg_offset+2]), 0xFF)
    ptp_flag = and(strtonum("0x"ptp[msg_offset+3]), 0xFF)
    ptp_cf = strtonum("0x"ptp[msg_offset+4]""ptp[msg_offset+5]""ptp[msg_offset+6]""ptp[msg_offset+7])/65536
    ptp_seq = strtonum("0x"ptp[msg_offset+15])
    ptp_control = and(rshift(strtonum("0x"ptp[msg_offset+16]),8), 0xFF)
    ptp_log_interval = and(strtonum("0x"ptp[msg_offset+16]), 0xFF)
    if (ptp_log_interval > 128) ptp_log_interval -= 256

    dumpMac(ptp_msg_type[msg_type], ptp)
    printf "%s\tDomain\t%d\n", ptp_msg_type[msg_type], ptp_domain
    printf "%s\tFlag\t%d\n", ptp_msg_type[msg_type], ptp_flag
    printf "%s\tCF\t%d\n", ptp_msg_type[msg_type], ptp_cf
    printf "%s\tSeq\t%d\n", ptp_msg_type[msg_type], ptp_seq
    printf "%s\tCtrl\t%d\n", ptp_msg_type[msg_type], ptp_control
    printf "%s\tIntvl\t%d\n", ptp_msg_type[msg_type], ptp_log_interval

    if (ptp_msg_type[msg_type] == "SYNC") {
        t1_s = strtonum("0x"ptp[ptp_body_offset+1]""ptp[ptp_body_offset+2])
        t1_ns = strtonum("0x"ptp[ptp_body_offset+3]""ptp[ptp_body_offset+4])
        ptp_tlv_offset = ptp_body_offset + 6
        delay_offset = ptp_tlv_offset + ptp_tlv_delay_offset
        intertal_delay = ptp[delay_offset]""ptp[delay_offset+1]
        t2_offset = ptp_tlv_offset+ptp_tlv_timestamp_offset
        #strnum has precision loss for 64bit number, so here invoke python to do the job
        t2 = "0x"ptp[t2_offset]""ptp[t2_offset+1]""ptp[t2_offset+2]""ptp[t2_offset+3]
        #printf " t1 %d %09d t2 %d %09d intdly %s", t1_s, t1_ns, t2/1000000000, t2%1000000000, intertal_delay
        printf "SYNC\tt1\t%d %09d\n", t1_s, t1_ns
        printf "SYNC\tt2\t"
        cmd = "python -c 'print "t2"/1000000000, "t2"%1000000000'"
        system(cmd)
        printf "SYNC\tdelay\t%s\n", intertal_delay
    }
    else if (ptp_msg_type[msg_type] == "FLOW") {
        t1_s = strtonum("0x"ptp[ptp_body_offset+1]""ptp[ptp_body_offset+2])
        t1_ns = strtonum("0x"ptp[ptp_body_offset+3]""ptp[ptp_body_offset+4])
        printf "FLOW\tt1\t%d %09d\n", t1_s, t1_ns
    }
    else if (ptp_msg_type[msg_type] == "REQ") {
        t3_s = strtonum("0x"ptp[ptp_body_offset+1]""ptp[ptp_body_offset+2])
        t3_ns = strtonum("0x"ptp[ptp_body_offset+3]""ptp[ptp_body_offset+4])
        printf "REQ\tt3\t%d %09d\n", t3_s, t3_ns
    }
    else if (ptp_msg_type[msg_type] == "RESP") {
        t4_s = strtonum("0x"ptp[ptp_body_offset+1]""ptp[ptp_body_offset+2])
        t4_ns = strtonum("0x"ptp[ptp_body_offset+3]""ptp[ptp_body_offset+4])
        printf "RESP\tt4\t%d %09d\n", t4_s, t4_ns
    }
    ptp_counter[msg_type]++
    printf "\n"
}

function dumpCFM(cfm)
{
    dumpMac("CFM", cfm)
    printf "\n"
}

function dumpSYNCE(synce)
{
    dumpMac("SYNCE", synce)

    ituoui = substr(pkt[eth_type_offset+1],3)"-"substr(pkt[eth_type_offset+2],1,2)"-"substr(pkt[eth_type_offset+2],3)
    itusubtype = strtonum("0x"pkt[eth_type_offset+3])
    pduflag = substr(pkt[eth_type_offset+4],1,2)
    if (pduflag == "18") pduflagstr = "event"
    else if (pduflag == "10") pduflagstr = "infomation"
    else pdflagstr = "unk("pduflag")"
    tlvtype = rshift(strtonum("0x"pkt[eth_type_offset+6]),8)
    ssmcode = and(strtonum("0x"pkt[eth_type_offset+7]),0xFF)

    switch (ssmcode) {
        case 0: ssm = "SDH-UNK"; break
        case 2: ssm = "SDH-PRC"; break
        case 4: ssm = "SDH-SSUA"; break
        case 8: ssm = "SDH-SSUB"; break
        case 11: ssm = "SDH-SEC"; break
        case 15: ssm = "SDH-DNU"; break
        case 16: ssm = "SDH-LOS"; break
        case 255: ssm = "SDH-NONE"; break
        case 1:
        case 3:
        case 5:
        case 6:
        case 7:
        case 9:
        case 10:
        case 12:
        case 13:
        case 14: ssm = "SDH-RES"; break
        default: ssm = "SDH-INV"; break
    }

    synce_counter++

    printf "SYNCE\tOUI\t%s\n", ituoui
    printf "SYNCE\tSUB\t%d\n", itusubtype
    printf "SYNCE\tPDU\t%s\n", pduflagstr
    printf "SYNCE\tTLV\t%d\n", tlvtype
    printf "SYNCE\tSSM\t%s(%d)\n", ssm, ssmcode

    printf "\n"
}

function dumpLAG(lag)
{
    dumpMac("LAG", lag)
    printf "\n"
}

