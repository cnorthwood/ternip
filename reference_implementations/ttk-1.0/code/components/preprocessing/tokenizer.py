import re
from abbreviation import *


     
def Split_Punctuation(token):
    """Split punctuation at beginning and end of token. Maximum of
    three punctuation marks at end of token is allowed. Possibly
    better not to split closing brackets if token contains
    corresponding closing bracket (but what about putting one word
    between brackets --> exception)."""
    token = re.sub(r'(([.,!?\'\`\";:]|[\]\[\(\){}])$)', r' \1', token)
    token = re.sub(r'(([.,!?\'\`\";:]|[\]\[\(\){}]) .$)', r' \1', token)
    token = re.sub(r'(([.,!?\'\`\";:]|[\]\[\(\){}]) . .$)', r' \1', token)
    token = re.sub(r'(^([.,!?\'\`\";:]|[\]\[\(\){}]))', r'\1 ', token)
    token = re.sub(r'(^. ([.,!?\'\`\";:]|[\]\[\(\){}]))', r'\1 ', token)
    token = re.sub(r'(^. . ([.,!?\'\`\";:]|[\]\[\(\){}]))', r'\1 ', token)
    return token


def Restore_Abbrevs(token):
    """Restore abbreviations. If a period is preceded by a number of
    non-whitespace characters, then check whether those characters
    with the period are an abbreviation. If so, glue them back
    together."""
    pattern = re.compile(r'(\S+) \.')
    found = pattern.search(token)
    if found:
        tmp = found.group(1)+ '.'
        if Abbrev(tmp):
            token = pattern.sub(r'\1.', token)
    return token


def Abbrev(token):
    """Abbreviation Lookup. A token is an abbreviation either if it is
    on the abbrevs list or if it matches the regular expression
    /(^[A-Z]\.)+/, which encodes initials."""
    pattern = re.compile(r'^([A-Z]\.)+$')
    found = pattern.search(token)
    return ((token in abbrevs) or found)


def Add_EOS_Marker(token, i, line):
   
    """Adding end-of-sentence markers (ie newlines). First check for a
    space followed by a period, exclamation mark or question
    mark. These may be followed by one other punctuation, which is
    either a quote or a closing bracket. Otherwise check whether the
    token is a possible sentence-final abbreviations followed by a
    possible sentence-intitial token. In other cases there will be no
    end-of-sentence."""
    pattern = re.compile(r' [.!?]( [")])?$')
    found = pattern.search(token)
    if found:
        token = token + '\n'
    elif ((token in end_abbrevs) and i<(len(line)-1) and (line[i+1] in initial_tokens)):
        token = token + '\n'
    else: 
        token = token + ' '
    return token
    

def Split_Contractions(token):
    re_pattern = re.compile(r"(\w+)'re ", re.IGNORECASE)
    t_pattern  = re.compile(r"(\w+)'t ", re.IGNORECASE)
    ll_pattern = re.compile(r"(\w+)'ll ", re.IGNORECASE)
    ve_pattern = re.compile(r"(\w+)'ve ", re.IGNORECASE)
    d_pattern  = re.compile(r"(\w+)'d ", re.IGNORECASE)
    s_pattern  = re.compile(r"(\w+)'s ", re.IGNORECASE)
    m_pattern  = re.compile(r"(\w+)'m ", re.IGNORECASE)
#   $token =~ s/(\S+)\'s /$1 \'s /; # hack for for possessive 's
    posse_pattern = re.compile(r"(\S+)'s ", re.IGNORECASE) 
    token = re_pattern.sub(r"\1 're ", token)
    token =  t_pattern.sub(r"\1 't ", token)
    token = ll_pattern.sub(r"\1 'll ", token)
    token = ve_pattern.sub(r"\1 've ", token)
    token =  d_pattern.sub(r"\1 'd ", token)
    token =  s_pattern.sub(r"\1 's ", token)
    token =  m_pattern.sub(r"\1 'm ", token)
    token = posse_pattern.sub(r"\1 's ", token)
    return token


def Tokenize_File(in_name, out_name):
    
    global token_newline
    token_newline = ''
    
    in_file = open(in_name,'r')
    out_file = open(out_name,'w')
    
    line = in_file.readline()
    while(line):
        line = re.sub(r'^\s+', '', line)
        line = re.sub(r'\s+$', '', line)
        found_para = re.search(r'^<P>', line)
        if(found_para):
            line = re.sub(r'^<P>', r'', line)
            out_file.write('\n<P>\n\n')
        
        #original delimiter is r'\s+'. I think this would make no difference
        #by default the separator for split is 
        #"arbitrary strings of whitespace characters (space, tab, newline, return, formfeed)."     
        #@line = split /\s+/ , $line; # put tokens on array
        line_list = line.split()  
        index_count = 0
        for token in line_list:
            found_punc = re.search(r'([.,!?\'\`\";:]|[\]\[\(\){}])', token)
            if(found_punc):
                token = Split_Punctuation(token)
                token = Restore_Abbrevs(token)
                token = Add_EOS_Marker(token, index_count, line_list)
            else:
                token = token + ' '
                      
            token = Split_Contractions(token)
            out_file.write(token)      
            index_count = index_count + 1
            token_newline = token[:]
            
        found_newline = re.search(r'\n', token_newline)
        if(found_newline):
            out_file.write('\n')
        else:
            out_file.write('\n\n')

        line = in_file.readline()
        
    in_file.close()
    out_file.close()



if __name__ == '__main__':
    in_file = 'C:\Documents and Settings\Tom\Desktop\Tokenize\APW19990506.0155.tml'
    out_file = 'C:\Documents and Settings\Tom\Desktop\Tokenize\test.txt'
    Tokenize_file(in_file, out_file)
    
